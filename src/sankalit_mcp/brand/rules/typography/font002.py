from docx.shared import Pt
from sankalit_mcp.brand.models import BrandRule, RuleCategory, Severity, ValidationResult
from sankalit_mcp.brand.context import ValidationContext
from sankalit_mcp.brand.rules.base_rule import BaseRule
from sankalit_mcp.styles.style_engine import StyleEngine


class Font002Rule(BaseRule):

    @property
    def metadata(self) -> BrandRule:
        return BrandRule(
            id="FONT002",
            name="Heading Font Linter",
            category=RuleCategory.TYPOGRAPHY,
            description="Ensure heading texts use the correct primary brand font family, size, and weights from the StyleConfig.",
            severity=Severity.ERROR,
            auto_fixable=True,
            version=1,
        )

    def _get_heading_level(self, style_name: str) -> int:
        if style_name.startswith("Heading "):
            try:
                return int(style_name.split(" ")[1])
            except (ValueError, IndexError):
                pass
        return 0

    def validate(self, context: ValidationContext) -> ValidationResult:
        doc = context.document
        style = context.style_config

        expected_font = style.fonts.font_family if style else "Calibri"

        # Walk heading paragraphs and check properties
        for idx, paragraph in enumerate(doc.paragraphs):
            level = self._get_heading_level(paragraph.style.name)
            if level <= 0:
                continue

            # Resolve expected size from TypographySection config
            if level == 1:
                cfg = style.typography.h1 if style else None
                expected_size = cfg.size if cfg else 14
            elif level == 2:
                cfg = style.typography.h2 if style else None
                expected_size = cfg.size if cfg else 12
            elif level == 3:
                cfg = style.typography.h3 if style else None
                expected_size = cfg.size if cfg else 11
            elif level == 4:
                cfg = style.typography.h4 if style else None
                expected_size = cfg.size if cfg else 11
            else:
                expected_size = 11

            for run_idx, run in enumerate(paragraph.runs):
                font_name = run.font.name
                font_size = run.font.size

                # Check explicit overrides on heading runs
                if font_name is not None and font_name != expected_font:
                    return ValidationResult(
                        rule_id=self.metadata.id,
                        passed=False,
                        expected=expected_font,
                        actual=font_name,
                        message=f"Heading paragraph {idx} run {run_idx} overrides font name to '{font_name}'.",
                    )
                if font_size is not None and font_size.pt != expected_size:
                    return ValidationResult(
                        rule_id=self.metadata.id,
                        passed=False,
                        expected=f"{expected_size}pt",
                        actual=f"{font_size.pt}pt",
                        message=f"Heading paragraph {idx} run {run_idx} overrides font size to {font_size.pt}pt.",
                    )

        return ValidationResult(
            rule_id=self.metadata.id,
            passed=True,
            expected="Calibri headings",
            actual="Calibri headings",
            message="Heading fonts are compliant.",
        )

    def fix(self, context: ValidationContext) -> None:
        doc = context.document
        style = context.style_config

        expected_font = style.fonts.font_family if style else "Calibri"

        for paragraph in doc.paragraphs:
            level = self._get_heading_level(paragraph.style.name)
            if level <= 0:
                continue

            if level == 1:
                cfg = style.typography.h1 if style else None
                expected_size = cfg.size if cfg else 14
            elif level == 2:
                cfg = style.typography.h2 if style else None
                expected_size = cfg.size if cfg else 12
            elif level == 3:
                cfg = style.typography.h3 if style else None
                expected_size = cfg.size if cfg else 11
            elif level == 4:
                cfg = style.typography.h4 if style else None
                expected_size = cfg.size if cfg else 11
            else:
                expected_size = 11

            # Fix paragraph-level heading style fonts
            style_name = f"Heading {level}"
            if style_name in doc.styles:
                style_font = doc.styles[style_name].font
                style_font.name = expected_font
                style_font.size = Pt(expected_size)

            for run in paragraph.runs:
                if run.font.name is not None and run.font.name != expected_font:
                    run.font.name = expected_font
                if run.font.size is not None and run.font.size.pt != expected_size:
                    run.font.size = Pt(expected_size)
