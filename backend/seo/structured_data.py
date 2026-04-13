"""
JSON-LD STRUCTURED DATA GENERATORS
Schema.org markup for products, categories, breadcrumbs, etc.
"""
import json
from typing import Optional, List, Dict, Any
from datetime import datetime


class StructuredDataGenerator:
    """Generate JSON-LD structured data for SEO"""

    def __init__(self, site_name: str = "OmniShop Vietnam", site_url: str = "https://omnishop.example.com"):
        self.site_name = site_name
        self.site_url = site_url

    def _base(self) -> Dict:
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": self.site_name,
            "url": self.site_url,
        }

    def product(
        self,
        product_id: str,
        name: str,
        description: str,
        price: float,
        currency: str = "VND",
        sku: Optional[str] = None,
        brand: Optional[str] = None,
        availability: str = "https://schema.org/InStock",
        image: Optional[str] = None,
        url: Optional[str] = None,
        rating: Optional[float] = None,
        review_count: Optional[int] = None,
        condition: str = "NewCondition",
    ) -> str:
        """Generate Product JSON-LD schema"""
        data = {
            "@type": "Product",
            "productID": product_id,
            "name": name,
            "description": description,
            "image": [image] if image else [],
            "url": url or self.site_url,
        }
        if sku:
            data["sku"] = sku
        if brand:
            data["brand"] = {"@type": "Brand", "name": brand}

        data["offers"] = {
            "@type": "Offer",
            "price": str(price),
            "priceCurrency": currency,
            "availability": availability,
            "url": url or self.site_url,
            "priceValidUntil": datetime.now().strftime("%Y-12-31"),
            "shippingDetails": {
                "@type": "OfferShippingDetails",
                "shippingDestination": {
                    "@type": "Country",
                    "name": "VN"
                },
                "deliveryTime": {
                    "@type": "ShippingDeliveryTime",
                    "handlingTime": {
                        "@type": "QuantitativeValue",
                        "minValue": "0",
                        "maxValue": "1",
                        "unitCode": "DAY"
                    },
                    "transitTime": {
                        "@type": "QuantitativeValue",
                        "minValue": "1",
                        "maxValue": "5",
                        "unitCode": "DAY"
                    }
                }
            }
        }

        if rating is not None:
            data["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": str(rating),
                "reviewCount": str(review_count or 0),
            }
            data["review"] = {
                "@type": "Review",
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": str(rating),
                },
                "author": {"@type": "Organization", "name": self.site_name}
            }

        return json.dumps(data, ensure_ascii=False)

    def breadcrumb_list(self, items: List[Dict[str, str]]) -> str:
        """Generate BreadcrumbList JSON-LD schema"""
        data = {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": item["name"],
                    "item": f"{self.site_url}{item['url']}" if item.get("url") else self.site_url,
                }
                for i, item in enumerate(items)
            ]
        }
        return json.dumps(data, ensure_ascii=False)

    def category_page(
        self,
        name: str,
        description: str,
        url: Optional[str] = None,
        image: Optional[str] = None,
    ) -> str:
        """Generate CollectionPage (category) JSON-LD schema"""
        data = {
            "@type": "CollectionPage",
            "name": name,
            "description": description,
            "url": url or self.site_url,
        }
        if image:
            data["image"] = image
        data["publisher"] = {"@type": "Organization", "name": self.site_name}
        return json.dumps(data, ensure_ascii=False)

    def website(self, site_search_url: Optional[str] = None) -> str:
        """Generate WebSite JSON-LD schema with sitelinks searchbox"""
        data = {
            "@type": "WebSite",
            "name": self.site_name,
            "url": self.site_url,
        }
        if site_search_url:
            data["potentialAction"] = {
                "@type": "SearchAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": f"{site_search_url}?q={{search_term_string}}",
                },
                "query-input": "required name=search_term_string",
            }
        return json.dumps(data, ensure_ascii=False)

    def organization(self) -> str:
        """Generate Organization JSON-LD schema"""
        return json.dumps(self._base(), ensure_ascii=False)

    def local_business(
        self,
        name: str,
        address: str,
        phone: str,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
    ) -> str:
        """Generate LocalBusiness JSON-LD schema"""
        data = {
            "@type": "LocalBusiness",
            "name": name,
            "telephone": phone,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": address,
                "addressCountry": "VN",
            },
        }
        if lat and lng:
            data["geo"] = {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng}
        return json.dumps(data, ensure_ascii=False)

    def faq(self, questions: List[Dict[str, str]]) -> str:
        """Generate FAQPage JSON-LD schema"""
        data = {
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q["question"],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": q["answer"],
                    }
                }
                for q in questions
            ]
        }
        return json.dumps(data, ensure_ascii=False)

    def product_list(
        self,
        name: str,
        description: str,
        url: Optional[str] = None,
        items: Optional[List[Dict]] = None,
    ) -> str:
        """Generate ItemList JSON-LD schema"""
        data = {
            "@type": "ItemList",
            "name": name,
            "description": description,
            "url": url or self.site_url,
        }
        if items:
            data["itemListElement"] = [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "url": f"{self.site_url}{item.get('url', '')}",
                }
                for i, item in enumerate(items)
            ]
        return json.dumps(data, ensure_ascii=False)


# Global instance
_sd_generator: Optional[StructuredDataGenerator] = None


def get_sd_generator() -> StructuredDataGenerator:
    global _sd_generator
    if _sd_generator is None:
        _sd_generator = StructuredDataGenerator()
    return _sd_generator
