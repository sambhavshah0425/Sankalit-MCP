from sankalit_mcp.brand.models import BrandRule, RuleCategory, Severity, ValidationResult
from sankalit_mcp.brand.context import ValidationContext
from sankalit_mcp.brand.rules.base_rule import BaseRule


class Cover001Rule(BaseRule):

    @property
    def metadata(self) -> BrandRule:
        return BrandRule(
            id="COVER001",
            name="Cover Page Linter",
            category=RuleCategory.COVER,
            description="Ensure the document starts with a standard Cover Page containing metadata tables and key assumptions.",
            severity=Severity.ERROR,
            auto_fixable=False,
            version=1,
        )

    def validate(self, context: ValidationContext) -> ValidationResult:
        doc = context.document
        
        # Check first 20 paragraphs and first 3 tables for cover page tags
        cover_content = ""
        for p in doc.paragraphs[:20]:
            cover_content += p.text + "\n"
            
        for table in doc.tables[:3]:
            for row in table.rows:
                for cell in row.cells:
                    cover_content += cell.text + "\n"

        has_doc_control = "Document Control" in cover_content
        has_assumptions = "Key Assumptions" in cover_content

        passed = has_doc_control and has_assumptions

        return ValidationResult(
            rule_id=self.metadata.id,
            passed=passed,
            expected="Document Control & Key Assumptions on cover",
            actual=f"DocControl: {has_doc_control}, Assumptions: {has_assumptions}",
            message="Cover Page layout elements are compliant." if passed else "Document lacks standard Cover Page components.",
        )

    def fix(self, context: ValidationContext) -> None:
        pass
