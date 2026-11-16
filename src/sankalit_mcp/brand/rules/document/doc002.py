from docx.shared import Mm
from sankalit_mcp.brand.models import BrandRule, RuleCategory, Severity, ValidationResult
from sankalit_mcp.brand.context import ValidationContext
from sankalit_mcp.brand.rules.base_rule import BaseRule


class Doc002Rule(BaseRule):

    @property
    def metadata(self) -> BrandRule:
        return BrandRule(
            id="DOC002",
            name="Bottom Margin Linter",
            category=RuleCategory.DOCUMENT,
            description="Ensure the bottom margin complies with the StyleConfig standard.",
            severity=Severity.ERROR,
            auto_fixable=True,
            version=1,
        )

    def validate(self, context: ValidationContext) -> ValidationResult:
        doc = context.document
        style = context.style_config

        # Standard bottom margin in mm is 20.0
        expected_bottom = style.document.margins["bottom"] if style else 20.0

        for idx, section in enumerate(doc.sections):
            actual_bottom_mm = round(section.bottom_margin.mm, 1)
            if abs(actual_bottom_mm - expected_bottom) > 0.5:
                return ValidationResult(
                    rule_id=self.metadata.id,
                    passed=False,
                    expected=f"{expected_bottom} mm",
                    actual=f"{actual_bottom_mm} mm",
                    message=f"Section {idx} bottom margin of {actual_bottom_mm}mm deviates from expected {expected_bottom}mm.",
                )

        return ValidationResult(
            rule_id=self.metadata.id,
            passed=True,
            expected=f"{expected_bottom} mm",
            actual=f"{expected_bottom} mm",
            message="Bottom margins are compliant.",
        )

    def fix(self, context: ValidationContext) -> None:
        doc = context.document
        style = context.style_config

        expected_bottom = style.document.margins["bottom"] if style else 20.0

        for section in doc.sections:
            section.bottom_margin = Mm(expected_bottom)
