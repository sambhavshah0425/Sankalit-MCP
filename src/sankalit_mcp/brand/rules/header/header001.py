from sankalit_mcp.brand.models import BrandRule, RuleCategory, Severity, ValidationResult
from sankalit_mcp.brand.context import ValidationContext
from sankalit_mcp.brand.rules.base_rule import BaseRule


class Header001Rule(BaseRule):

    @property
    def metadata(self) -> BrandRule:
        return BrandRule(
            id="HEADER001",
            name="Header Linter",
            category=RuleCategory.HEADER,
            description="Ensure the document sections have branded header layouts.",
            severity=Severity.WARNING,
            auto_fixable=False,
            version=1,
        )

    def validate(self, context: ValidationContext) -> ValidationResult:
        doc = context.document

        for idx, section in enumerate(doc.sections):
            # Cover page headers can be different/empty.
            # Skip check on first section if different_first_page_header_footer is enabled
            if idx == 0 and getattr(section, "different_first_page_header_footer", False):
                continue

            header_text = "".join(p.text.strip() for p in section.header.paragraphs)
            has_header_content = (len(header_text) > 10) or bool(section.header.tables)
            if not has_header_content:
                return ValidationResult(
                    rule_id=self.metadata.id,
                    passed=False,
                    expected="Branded header content (>10 chars or table)",
                    actual=f"Header text length: {len(header_text)}, tables: {len(section.header.tables)}",
                    message=f"Section {idx} header lacks substantial branded text or table layout content.",
                )

        return ValidationResult(
            rule_id=self.metadata.id,
            passed=True,
            expected="Branded header content",
            actual="Branded header content",
            message="Section headers contain layout elements.",
        )

    def fix(self, context: ValidationContext) -> None:
        pass
