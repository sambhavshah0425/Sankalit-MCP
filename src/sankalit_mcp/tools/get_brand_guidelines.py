from sankalit_mcp.services.brand.brand_cache import BrandCache

def get_brand_guidelines() -> str:
    """
    Get the compiled markdown branding guidelines and layout rules for Sankalit Consultant documents.
    """
    return BrandCache.load_instructions()
