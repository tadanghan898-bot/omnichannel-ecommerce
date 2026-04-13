"""
ULTIMATE E-COMMERCE - Platform Configuration
Determines which modules are active based on PLATFORM_MODE
"""
from backend.database import settings


# Module availability based on platform mode
PLATFORM_MODES = {
    "BASIC": {
        "multi_vendor": False,
        "multi_tenant": False,
        "social": False,
        "ai_engine": False,
        "dropship": False,
        "description": "Basic e-commerce - cart, checkout, products",
    },
    "MARKETPLACE": {
        "multi_vendor": True,
        "multi_tenant": False,
        "social": False,
        "ai_engine": False,
        "dropship": False,
        "description": "Multi-vendor marketplace",
    },
    "SAAS": {
        "multi_vendor": False,
        "multi_tenant": True,
        "social": False,
        "ai_engine": False,
        "dropship": False,
        "description": "SaaS multi-tenant platform",
    },
    "SOCIAL": {
        "multi_vendor": False,
        "multi_tenant": False,
        "social": True,
        "ai_engine": False,
        "dropship": False,
        "description": "Social commerce with livestream",
    },
    "AI_STORE": {
        "multi_vendor": False,
        "multi_tenant": False,
        "social": False,
        "ai_engine": True,
        "dropship": False,
        "description": "AI-powered store",
    },
    "DROPSHIPPING": {
        "multi_vendor": False,
        "multi_tenant": False,
        "social": False,
        "ai_engine": False,
        "dropship": True,
        "description": "Dropshipping automation",
    },
    "ULTIMATE": {
        "multi_vendor": True,
        "multi_tenant": True,
        "social": True,
        "ai_engine": True,
        "dropship": True,
        "description": "All features enabled - the ultimate platform",
    },
}


def is_module_active(module_name: str) -> bool:
    """Check if a module is active for current platform mode"""
    mode = settings.PLATFORM_MODE.upper()
    if mode not in PLATFORM_MODES:
        mode = "ULTIMATE"
    return PLATFORM_MODES[mode].get(module_name, False)


def get_active_modules() -> dict:
    """Get all active modules for current platform"""
    mode = settings.PLATFORM_MODE.upper()
    if mode not in PLATFORM_MODES:
        mode = "ULTIMATE"
    return PLATFORM_MODES[mode]


def get_platform_info() -> dict:
    """Get current platform information"""
    mode = settings.PLATFORM_MODE.upper()
    if mode not in PLATFORM_MODES:
        mode = "ULTIMATE"
    info = PLATFORM_MODES[mode].copy()
    info["mode"] = mode
    info["active_features"] = [k for k, v in info.items() if isinstance(v, bool) and v]
    return info
