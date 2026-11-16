from sankalit_mcp.brand.models import BrandRule, RuleCategory, Severity, ValidationResult
from sankalit_mcp.brand.context import ValidationContext
from sankalit_mcp.brand.rules.base_rule import BaseRule


class Footer001Rule(BaseRule):

    @property
    def metadata(self) -> BrandRule:
        return BrandRule(
            id="FOOTER001",
            name="Footer Linter",
            category=RuleCategory.FOOTER,
            description="Ensure the document sections have branded footer layouts.",
            severity=Severity.WARNING,
            auto_fixable=False,
            version=1,
        )

    def validate(self, context: ValidationContext) -> ValidationResult:
        doc = context.document

        for idx, section in enumerate(doc.sections):
            if idx == 0 and getattr(section, "different_first_page_header_footer", False):
                continue

            has_footer_content = any(p.text.strip() for p in section.footer.paragraphs) or bool(section.footer.tables)
            if not has_footer_content:
                return ValidationResult(
                    rule_id=self.metadata.id,
                    passed=False,
                    expected="Branded footer content",
                    actual="Empty footer",
                    message=f"Section {idx} footer has no text or table layout content.",
                )

        return ValidationResult(
            rule_id=self.metadata.id,
            passed=True,
            expected="Branded footer content",
            actual="Branded footer content",
            message="Section footers contain layout elements.",
        )

    def fix(self, context: ValidationContext) -> None:
        pass
