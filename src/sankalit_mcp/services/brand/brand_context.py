from dataclasses import dataclass
from sankalit_mcp.services.brand.brand_cache import BrandCache


@dataclass
class GenerationRequest:
    user_prompt: str
    brand_instructions: str
    template_name: str


class BrandContext:

    @classmethod
    def build_generation_request(cls, user_prompt: str, template_name: str) -> GenerationRequest:
        instructions = BrandCache.load_instructions()
        return GenerationRequest(
            user_prompt=user_prompt,
            brand_instructions=instructions,
            template_name=template_name
        )
