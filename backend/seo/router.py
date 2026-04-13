"""
SEO Router - Sitemap, Robots.txt, Structured Data endpoints
"""
from fastapi import APIRouter, Depends, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
import json

from backend.database import get_db
from backend.models.product import Product, Category
from backend.seo.structured_data import get_sd_generator
from backend.seo.sitemap import SitemapGenerator, generate_robots_txt

router = APIRouter(prefix="/api/seo", tags=["SEO"])


@router.get("/sitemap.xml")
async def sitemap_xml(db: Session = Depends(get_db)):
    """Generate XML sitemap for all products and categories"""
    site_url = "https://omnishop.example.com"
    gen = SitemapGenerator(site_url)

    # Get active products
    products = db.execute(
        select(Product).where(Product.status == "active").limit(10000)
    ).scalars().all()
    product_data = [
        {"id": p.id, "slug": p.slug, "updated_at": p.updated_at}
        for p in products
    ]

    # Get categories
    categories = db.execute(
        select(Category).where(Category.is_active == True)
    ).scalars().all()
    cat_data = [
        {"id": c.id, "slug": c.slug, "updated_at": c.updated_at}
        for c in categories
    ]

    product_sitemap = gen.generate_product_sitemap(product_data)
    category_sitemap = gen.generate_category_sitemap(cat_data)

    index = gen.generate_index([
        {"loc": f"{site_url}/api/seo/sitemap-products.xml", "lastmod": ""},
        {"loc": f"{site_url}/api/seo/sitemap-categories.xml", "lastmod": ""},
    ])

    return Response(
        content=index,
        media_type="application/xml"
    )


@router.get("/sitemap-products.xml")
async def sitemap_products_xml(db: Session = Depends(get_db)):
    """Product-only sitemap"""
    site_url = "https://omnishop.example.com"
    gen = SitemapGenerator(site_url)

    products = db.execute(
        select(Product).where(Product.status == "active").limit(10000)
    ).scalars().all()
    product_data = [
        {"id": p.id, "slug": p.slug, "updated_at": p.updated_at}
        for p in products
    ]

    content = gen.generate_product_sitemap(product_data)
    return Response(content=content, media_type="application/xml")


@router.get("/sitemap-categories.xml")
async def sitemap_categories_xml(db: Session = Depends(get_db)):
    """Category-only sitemap"""
    site_url = "https://omnishop.example.com"
    gen = SitemapGenerator(site_url)

    categories = db.execute(
        select(Category).where(Category.is_active == True)
    ).scalars().all()
    cat_data = [
        {"id": c.id, "slug": c.slug, "updated_at": c.updated_at}
        for c in categories
    ]

    content = gen.generate_category_sitemap(cat_data)
    return Response(content=content, media_type="application/xml")


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    """Generate robots.txt"""
    site_url = "https://omnishop.example.com"
    return generate_robots_txt(
        site_url=site_url,
        sitemap_url=f"{site_url}/api/seo/sitemap.xml"
    )


@router.get("/structured-data/product/{product_id}")
async def product_structured_data(product_id: int, db: Session = Depends(get_db)):
    """Get JSON-LD structured data for a product"""
    product = db.get(Product, product_id)
    if not product:
        return {"error": "Product not found"}

    sd_gen = get_sd_generator()
    images = []
    if product.images:
        try:
            images = json.loads(product.images) if isinstance(product.images, str) else product.images
        except (json.JSONDecodeError, TypeError):
            images = []

    schema = sd_gen.product(
        product_id=str(product.id),
        name=product.name,
        description=product.description or "",
        price=product.price,
        currency="VND",
        sku=product.sku,
        brand=product.brand.name if product.brand else None,
        availability="https://schema.org/InStock" if product.stock > 0 else "https://schema.org/OutOfStock",
        image=images[0].get("url") if images else None,
        url=f"/products/{product.slug}",
        rating=product.rating,
        review_count=product.review_count,
    )
    return {"json_ld": schema}


@router.get("/structured-data/category/{category_id}")
async def category_structured_data(category_id: int, db: Session = Depends(get_db)):
    """Get JSON-LD structured data for a category"""
    category = db.get(Category, category_id)
    if not category:
        return {"error": "Category not found"}

    sd_gen = get_sd_generator()
    schema = sd_gen.category_page(
        name=category.name,
        description=category.description or "",
        url=f"/category/{category.slug}",
    )
    return {"json_ld": schema}


@router.get("/structured-data/website")
async def website_structured_data():
    """Get WebSite JSON-LD with search box"""
    sd_gen = get_sd_generator()
    schema = sd_gen.website(site_search_url="/search")
    return {"json_ld": schema}
