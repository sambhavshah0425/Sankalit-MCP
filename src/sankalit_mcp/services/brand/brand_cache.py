import json
from pathlib import Path
from sankalit_mcp.config import PROJECT_ROOT


class BrandCache:
    _dir = PROJECT_ROOT / "resources" / "brand"

    @classmethod
    def load_instructions(cls) -> str:
        path = cls._dir / "brand_instructions.md"
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    @classmethod
    def load_manifest(cls) -> dict:
        path = cls._dir / "brand_manifest.json"
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
