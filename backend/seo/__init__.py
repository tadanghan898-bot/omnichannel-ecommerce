"""
SEO MODULE - Meta Tags, Structured Data, Sitemap, Robots
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

DEFAULT_SITE_NAME = "OmniShop Vietnam"
DEFAULT_SITE_URL = "https://omnishop.example.com"
DEFAULT_IMAGE = "https://omnishop.example.com/og-image.jpg"
DEFAULT_DESCRIPTION = "Mua sắm đa nền tảng - Lazada, Shopee, TikTok Shop, Facebook. Giá tốt nhất, giao hàng nhanh."
DEFAULT_KEYWORDS = ["mua sắm", "lazada", "shopee", "tiktok shop", "facebook shop", "thương mại điện tử", "dropshipping"]


class MetaGenerator:
    """Generate SEO meta tags for any page"""

    def __init__(
        self,
        site_name: str = DEFAULT_SITE_NAME,
        site_url: str = DEFAULT_SITE_URL,
        default_image: str = DEFAULT_IMAGE,
        default_description: str = DEFAULT_DESCRIPTION,
        default_keywords: str = None,
    ):
        self.site_name = site_name
        self.site_url = site_url
        self.default_image = default_image
        self.default_description = default_description
        self.default_keywords = default_keywords or ", ".join(DEFAULT_KEYWORDS)

    def generate(
        self,
        title: str,
        description: Optional[str] = None,
        url: Optional[str] = None,
        image: Optional[str] = None,
        keywords: Optional[str] = None,
        canonical: Optional[str] = None,
        noindex: bool = False,
        nofollow: bool = False,
        type: str = "website",
        author: Optional[str] = None,
        published_time: Optional[str] = None,
        modified_time: Optional[str] = None,
        section: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Generate all meta tags for a page"""
        full_title = f"{title} | {self.site_name}" if title else self.site_name
        desc = description or self.default_description
        og_image = image or self.default_image
        page_url = f"{self.site_url}{url}" if url else self.site_url
        canonical_url = canonical or page_url

        robots = []
        if noindex:
            robots.append("noindex")
        if nofollow:
            robots.append("nofollow")

        tags_html = " ".join(f'<meta name="keywords" content="{k}">' if i == 0 else k
                             for i, k in enumerate((keywords or self.default_keywords).split(","))) if keywords else ""

        return {
            # Standard meta
            "title": full_title,
            "description": desc,
            "keywords": keywords or self.default_keywords,
            "canonical": canonical_url,
            "robots": ", ".join(robots) if robots else "index, follow",
            "author": author or self.site_name,
            # Open Graph
            "og_title": full_title,
            "og_description": desc,
            "og_url": page_url,
            "og_image": og_image,
            "og_type": type,
            "og_site_name": self.site_name,
            # Twitter Card
            "twitter_card": "summary_large_image",
            "twitter_title": full_title,
            "twitter_description": desc,
            "twitter_image": og_image,
            "twitter_site": "@omnishop",
            # Article specific
            "article_published_time": published_time or "",
            "article_modified_time": modified_time or "",
            "article_author": author or "",
            "article_section": section or "",
            "article_tags": ",".join(tags) if tags else "",
        }

    def product_meta(
        self,
        name: str,
        description: str,
        price: float,
        currency: str = "VND",
        sku: Optional[str] = None,
        brand: Optional[str] = None,
        availability: str = "in_stock",
        condition: str = "new",
        url: Optional[str] = None,
        image: Optional[str] = None,
        rating: Optional[float] = None,
        review_count: Optional[int] = None,
    ) -> Dict[str, str]:
        """Generate SEO meta for a product page"""
        price_str = f"{price:,.0f} {currency}"
        meta = self.generate(
            title=name,
            description=description,
            url=url,
            image=image,
            type="product",
        )
        meta.update({
            "product_price": price_str,
            "product_sku": sku or "",
            "product_brand": brand or "",
            "product_availability": availability,
            "product_condition": condition,
            "product_rating_value": str(rating) if rating else "",
            "product_review_count": str(review_count) if review_count else "",
        })
        return meta


# Global generator instance
_meta_generator: Optional[MetaGenerator] = None


def get_meta_generator() -> MetaGenerator:
    global _meta_generator
    if _meta_generator is None:
        _meta_generator = MetaGenerator()
    return _meta_generator


def init_seo(site_name: str = None, site_url: str = None, default_image: str = None):
    global _meta_generator
    _meta_generator = MetaGenerator(
        site_name=site_name or DEFAULT_SITE_NAME,
        site_url=site_url or DEFAULT_SITE_URL,
        default_image=default_image or DEFAULT_IMAGE,
    )
