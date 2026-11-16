from docx.shared import Mm
from sankalit_mcp.brand.models import BrandRule, RuleCategory, Severity, ValidationResult
from sankalit_mcp.brand.context import ValidationContext
from sankalit_mcp.brand.rules.base_rule import BaseRule


class Doc001Rule(BaseRule):

    @property
    def metadata(self) -> BrandRule:
        return BrandRule(
            id="DOC001",
            name="Top Margin Linter",
            category=RuleCategory.DOCUMENT,
            description="Ensure the top margin complies with the StyleConfig standard.",
            severity=Severity.ERROR,
            auto_fixable=True,
            version=1,
        )

    def validate(self, context: ValidationContext) -> ValidationResult:
        doc = context.document
        style = context.style_config

        # Standard top margin in mm is 25.0
        expected_top = style.document.margins["top"] if style else 25.0

        for idx, section in enumerate(doc.sections):
            actual_top_mm = round(section.top_margin.mm, 1)
            if abs(actual_top_mm - expected_top) > 0.5:
                return ValidationResult(
                    rule_id=self.metadata.id,
                    passed=False,
                    expected=f"{expected_top} mm",
                    actual=f"{actual_top_mm} mm",
                    message=f"Section {idx} top margin of {actual_top_mm}mm deviates from expected {expected_top}mm.",
                )

        return ValidationResult(
            rule_id=self.metadata.id,
            passed=True,
            expected=f"{expected_top} mm",
            actual=f"{expected_top} mm",
            message="Top margins are compliant.",
        )

    def fix(self, context: ValidationContext) -> None:
        doc = context.document
        style = context.style_config

        expected_top = style.document.margins["top"] if style else 25.0

        for section in doc.sections:
            section.top_margin = Mm(expected_top)
