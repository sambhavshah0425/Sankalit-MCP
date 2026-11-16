from pathlib import Path

from sankalit_mcp.config import SUPPORTED_EXTENSIONS


def validate_extension(path: Path):
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {path.suffix}"
        )


def validate_parent_exists(path: Path):
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
