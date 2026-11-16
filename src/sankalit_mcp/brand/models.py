from dataclasses import dataclass, field
from enum import Enum
from typing import List


class RuleCategory(Enum):
    DOCUMENT = "document"
    TYPOGRAPHY = "typography"
    HEADER = "header"
    FOOTER = "footer"
    COVER = "cover"
    TOC = "toc"
    TABLE = "table"
    METADATA = "metadata"
    WATERMARK = "watermark"
    IMAGE = "image"


class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class BrandRule:
    id: str
    name: str
    category: RuleCategory
    description: str
    severity: Severity
    auto_fixable: bool
    version: int = 1
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    rule_id: str
    passed: bool
    expected: str
    actual: str
    message: str


@dataclass
class ComplianceReport:
    score: float
    grade: str
    execution_time_seconds: float
    total_executed: int
    passed_count: int
    warning_count: int
    error_count: int
    results: List[ValidationResult] = field(default_factory=list)
    fixes_applied: List[str] = field(default_factory=list)
