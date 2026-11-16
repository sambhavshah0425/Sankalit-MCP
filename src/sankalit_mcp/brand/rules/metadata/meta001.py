from sankalit_mcp.brand.models import BrandRule, RuleCategory, Severity, ValidationResult
from sankalit_mcp.brand.context import ValidationContext
from sankalit_mcp.brand.rules.base_rule import BaseRule


class Meta001Rule(BaseRule):

    @property
    def metadata(self) -> BrandRule:
        return BrandRule(
            id="META001",
            name="Title Property Linter",
            category=RuleCategory.METADATA,
            description="Ensure the document core properties contain a non-empty Title.",
            severity=Severity.INFO,
            auto_fixable=True,
            version=1,
        )

    def validate(self, context: ValidationContext) -> ValidationResult:
        doc = context.document
        title = doc.core_properties.title
        passed = bool(title and title.strip())

        return ValidationResult(
            rule_id=self.metadata.id,
            passed=passed,
            expected="Non-empty title metadata",
            actual=str(title),
            message="Core property Title is set." if passed else "Core property Title is empty or unset.",
        )

    def fix(self, context: ValidationContext) -> None:
        doc = context.document
        val_res = self.validate(context)
        if val_res.passed:
            return

        # Attempt to extract title from the first paragraph or Heading 1
        extracted_title = ""
        for p in doc.paragraphs:
            if p.text.strip():
                extracted_title = p.text.strip()
                break

        if extracted_title:
            doc.core_properties.title = extracted_title
        else:
            doc.core_properties.title = "Sankalit Technical Document"
