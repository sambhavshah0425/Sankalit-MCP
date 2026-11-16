from sankalit_mcp.brand.models import BrandRule, RuleCategory, Severity, ValidationResult
from sankalit_mcp.brand.context import ValidationContext
from sankalit_mcp.brand.rules.base_rule import BaseRule


class Wm001Rule(BaseRule):

    @property
    def metadata(self) -> BrandRule:
        return BrandRule(
            id="WM001",
            name="Draft Watermark Linter",
            category=RuleCategory.WATERMARK,
            description="Ensure watermark is set to DRAFT if document status is Draft.",
            severity=Severity.WARNING,
            auto_fixable=True,
            version=1,
        )

    def validate(self, context: ValidationContext) -> ValidationResult:
        doc = context.document
        is_draft = (context.revision == "Draft") or ("draft" in str(context.metadata.get("revision", "")).lower())

        if not is_draft:
            return ValidationResult(
                rule_id=self.metadata.id,
                passed=True,
                expected="N/A",
                actual="N/A",
                message="Non-draft document does not require DRAFT watermark.",
            )

        # Check section headers XML for watermark or text string "DRAFT"
        has_watermark = False
        for section in doc.sections:
            for p in section.header.paragraphs:
                if "DRAFT" in p.text or "DRAFT" in p._p.xml:
                    has_watermark = True
                    break

        return ValidationResult(
            rule_id=self.metadata.id,
            passed=has_watermark,
            expected="DRAFT watermark in header",
            actual="Present" if has_watermark else "Missing",
            message="Draft watermark is present in headers." if has_watermark else "Draft watermark is missing from headers.",
        )

    def fix(self, context: ValidationContext) -> None:
        doc = context.document
        is_draft = (context.revision == "Draft") or ("draft" in str(context.metadata.get("revision", "")).lower())
        if not is_draft:
            return

        for section in doc.sections:
            # Add simple DRAFT header paragraph text if not present
            header_p = section.header.paragraphs[0] if section.header.paragraphs else section.header.add_paragraph()
            if "DRAFT" not in header_p.text:
                header_p.text = "DRAFT - " + header_p.text
