from docx.shared import Pt
from sankalit_mcp.brand.models import BrandRule, RuleCategory, Severity, ValidationResult
from sankalit_mcp.brand.context import ValidationContext
from sankalit_mcp.brand.rules.base_rule import BaseRule
from sankalit_mcp.styles.style_engine import StyleEngine


class Font001Rule(BaseRule):

    @property
    def metadata(self) -> BrandRule:
        return BrandRule(
            id="FONT001",
            name="Body Font Linter",
            category=RuleCategory.TYPOGRAPHY,
            description="Ensure document body text uses the primary brand font family, size, and color from the StyleConfig.",
            severity=Severity.ERROR,
            auto_fixable=True,
            version=1,
        )

    def validate(self, context: ValidationContext) -> ValidationResult:
        doc = context.document
        style = context.style_config
        
        # Expected standards resolved from StyleConfig
        expected_font = style.fonts.font_family if style else "Calibri"
        expected_size = style.typography.body.size if style else 11
        expected_color = style.typography.body.color if style else "#333333"

        # Check default style configuration
        if "Normal" in doc.styles:
            normal_font = doc.styles["Normal"].font
            if normal_font.name != expected_font or (normal_font.size and normal_font.size.pt != expected_size):
                return ValidationResult(
                    rule_id=self.metadata.id,
                    passed=False,
                    expected=f"{expected_font} {expected_size}pt",
                    actual=f"{normal_font.name} {normal_font.size.pt if normal_font.size else 'None'}pt",
                    message="Document default Normal style font properties do not match the brand style standard.",
                )

        # Find first page break to skip cover page
        first_page_break_idx = -1
        for idx, paragraph in enumerate(doc.paragraphs):
            for run in paragraph.runs:
                if "w:br" in run._r.xml and 'type="page"' in run._r.xml:
                    first_page_break_idx = idx
                    break
            if first_page_break_idx != -1:
                break

        # Walk body paragraphs and inspect runs
        for idx, paragraph in enumerate(doc.paragraphs):
            # Skip cover page paragraphs
            if first_page_break_idx != -1 and idx <= first_page_break_idx:
                continue
            # Skip headings, TOC, and other metadata/section titles
            lower_text = paragraph.text.lower()
            if (paragraph.style.name.startswith("Heading") or 
                    "table of contents" in lower_text or 
                    "revision history" in lower_text or 
                    "abbreviations" in lower_text or 
                    "document control" in lower_text or 
                    "key assumptions" in lower_text):
                continue

            for run_idx, run in enumerate(paragraph.runs):
                font_name = run.font.name
                font_size = run.font.size

                # Detect explicit run overrides
                if font_name is not None and font_name != expected_font:
                    return ValidationResult(
                        rule_id=self.metadata.id,
                        passed=False,
                        expected=expected_font,
                        actual=font_name,
                        message=f"Body paragraph {idx} run {run_idx} overrides font family name to '{font_name}'.",
                    )
                if font_size is not None and font_size.pt != expected_size:
                    return ValidationResult(
                        rule_id=self.metadata.id,
                        passed=False,
                        expected=f"{expected_size}pt",
                        actual=f"{font_size.pt}pt",
                        message=f"Body paragraph {idx} run {run_idx} overrides font size to {font_size.pt}pt.",
                    )

        return ValidationResult(
            rule_id=self.metadata.id,
            passed=True,
            expected=f"{expected_font} {expected_size}pt",
            actual=f"{expected_font} {expected_size}pt",
            message="Body paragraph fonts and default styles are compliant.",
        )

    def fix(self, context: ValidationContext) -> None:
        doc = context.document
        style = context.style_config
        
        expected_font = style.fonts.font_family if style else "Calibri"
        expected_size = style.typography.body.size if style else 11
        expected_color = style.typography.body.color if style else "#333333"

        # Correct default style
        if "Normal" in doc.styles:
            normal_font = doc.styles["Normal"].font
            normal_font.name = expected_font
            normal_font.size = Pt(expected_size)
            if hasattr(StyleEngine, "hex_to_rgb"):
                normal_font.color.rgb = StyleEngine.hex_to_rgb(expected_color)

        # Clear explicit body run formatting overrides
        for paragraph in doc.paragraphs:
            if paragraph.style.name.startswith("Heading") or "table of contents" in paragraph.text.lower():
                continue
            for run in paragraph.runs:
                if run.font.name is not None and run.font.name != expected_font:
                    run.font.name = expected_font
                if run.font.size is not None and run.font.size.pt != expected_size:
                    run.font.size = Pt(expected_size)
