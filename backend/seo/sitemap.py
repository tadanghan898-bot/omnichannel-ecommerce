"""
SITEMAP & ROBOTS.TXT GENERATORS
"""
import xml.etree.ElementTree as ET
from typing import Optional, List, Dict
from datetime import datetime


class SitemapGenerator:
    """Generate XML sitemaps for SEO"""

    def __init__(self, site_url: str = "https://omnishop.example.com"):
        self.site_url = site_url.rstrip("/")

    def generate_product_sitemap(
        self,
        products: List[Dict],
        priority: float = 0.8,
        changefreq: str = "weekly",
    ) -> str:
        """Generate sitemap XML for product pages"""
        root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

        for p in products:
            url_elem = ET.SubElement(root, "url")
            loc = ET.SubElement(url_elem, "loc")
            loc.text = f"{self.site_url}/products/{p.get('slug', p.get('id', ''))}"

            if p.get("updated_at"):
                lastmod = ET.SubElement(url_elem, "lastmod")
                lastmod.text = p["updated_at"][:10] if isinstance(p["updated_at"], str) else str(p["updated_at"])

            priority_elem = ET.SubElement(url_elem, "priority")
            priority_elem.text = str(priority)

            changefreq_elem = ET.SubElement(url_elem, "changefreq")
            changefreq_elem.text = changefreq

        return ET.tostring(root, encoding="unicode", method="xml")

    def generate_category_sitemap(
        self,
        categories: List[Dict],
        priority: float = 0.6,
        changefreq: str = "weekly",
    ) -> str:
        """Generate sitemap XML for category pages"""
        root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

        for cat in categories:
            url_elem = ET.SubElement(root, "url")
            loc = ET.SubElement(url_elem, "loc")
            slug = cat.get("slug", cat.get("id", ""))
            loc.text = f"{self.site_url}/category/{slug}"

            if cat.get("updated_at"):
                lastmod = ET.SubElement(url_elem, "lastmod")
                lastmod.text = cat["updated_at"][:10] if isinstance(cat["updated_at"], str) else str(cat["updated_at"])

            priority_elem = ET.SubElement(url_elem, "priority")
            priority_elem.text = str(priority)

            changefreq_elem = ET.SubElement(url_elem, "changefreq")
            changefreq_elem.text = changefreq

        return ET.tostring(root, encoding="unicode", method="xml")

    def generate_index(self, sitemaps: List[Dict]) -> str:
        """Generate sitemap index XML"""
        root = ET.Element("sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

        for sm in sitemaps:
            sitemap_elem = ET.SubElement(root, "sitemap")
            loc = ET.SubElement(sitemap_elem, "loc")
            loc.text = sm["loc"]
            if sm.get("lastmod"):
                lastmod = ET.SubElement(sitemap_elem, "lastmod")
                lastmod.text = sm["lastmod"]

        return ET.tostring(root, encoding="unicode", method="xml")


def generate_robots_txt(
    site_url: str = "https://omnishop.example.com",
    allow_rules: Optional[List[str]] = None,
    disallow_rules: Optional[List[str]] = None,
    sitemap_url: Optional[str] = None,
) -> str:
    """Generate robots.txt content"""
    lines = ["User-agent: *"]

    disallow_rules = disallow_rules or [
        "/api/",
        "/admin/",
        "/checkout/",
        "/cart/",
        "/account/",
        "/?*sort=",
        "/?*page=",
    ]
    for rule in disallow_rules:
        lines.append(f"Disallow: {rule}")

    allow_rules = allow_rules or [
        "/api/products/",
        "/products/",
        "/categories/",
        "/brands/",
        "/search/",
    ]
    for rule in allow_rules:
        lines.append(f"Allow: {rule}")

    lines.append("")
    lines.append("Crawl-delay: 1")
    lines.append("")
    lines.append("User-agent: Googlebot")
    lines.append("Allow: /")
    lines.append("")

    lines.append("User-agent: Bingbot")
    lines.append("Allow: /")
    lines.append("Crawl-delay: 2")
    lines.append("")

    lines.append("User-agent: Slurp")
    lines.append("Allow: /")
    lines.append("Crawl-delay: 2")
    lines.append("")

    if sitemap_url:
        lines.append(f"Sitemap: {sitemap_url}")

    return "\n".join(lines)
