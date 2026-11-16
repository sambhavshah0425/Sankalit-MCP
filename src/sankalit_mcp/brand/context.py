from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from sankalit_mcp.styles.style_config import StyleConfig


@dataclass
class ValidationContext:
    document: Any
    style_config: Optional[StyleConfig] = None
    template_name: Optional[str] = None
    revision: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
