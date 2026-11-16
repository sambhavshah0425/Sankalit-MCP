from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from sankalit_mcp.brand.models import BrandRule, RuleCategory, Severity, ValidationResult
from sankalit_mcp.brand.context import ValidationContext
from sankalit_mcp.brand.rules.base_rule import BaseRule


class Toc001Rule(BaseRule):

    @property
    def metadata(self) -> BrandRule:
        return BrandRule(
            id="TOC001",
            name="Table of Contents Linter",
            category=RuleCategory.TOC,
            description="Ensure the document has an auto-generating Table of Contents field.",
            severity=Severity.ERROR,
            auto_fixable=True,
            version=1,
            dependencies=["FONT002"],
        )

    def validate(self, context: ValidationContext) -> ValidationResult:
        doc = context.document
        has_toc = False

        for p in doc.paragraphs:
            xml_str = p._p.xml
            if "w:instrText" in xml_str and "TOC" in xml_str:
                has_toc = True
                break

        return ValidationResult(
            rule_id=self.metadata.id,
            passed=has_toc,
            expected="Dynamic TOC Field Code",
            actual="TOC present" if has_toc else "TOC missing",
            message="Dynamic Table of Contents field code is present." if has_toc else "Table of Contents field is missing.",
        )

    def fix(self, context: ValidationContext) -> None:
        doc = context.document
        
        # Check if already present to prevent duplicate insertions
        val_res = self.validate(context)
        if val_res.passed:
            return

        # Find first heading or insert at paragraph index 2 (after cover title and revision history)
        insert_idx = 0
        for idx, p in enumerate(doc.paragraphs):
            if p.style.name == "Heading 1":
                insert_idx = idx
                break

        if insert_idx > 0:
            target_p = doc.paragraphs[insert_idx]
            p_hdr = target_p.insert_paragraph_before()
            p_toc = target_p.insert_paragraph_before()
        else:
            p_hdr = doc.add_paragraph()
            p_toc = doc.add_paragraph()

        # Render Table of Contents Heading
        p_hdr.paragraph_format.space_before = Pt(24)
        p_hdr.paragraph_format.space_after = Pt(12)
        style = context.style_config
        font_family = style.fonts.font_family if style else "Calibri"
        
        run_hdr = p_hdr.add_run("Table of Contents")
        run_hdr.font.name = font_family
        run_hdr.font.bold = True
        run_hdr.font.size = Pt(14)

        p_toc.paragraph_format.space_after = Pt(12)

        # Append TOC field codes
        p = p_toc._p
        run_begin = p.add_r()
        fldChar_begin = OxmlElement("w:fldChar")
        fldChar_begin.set(qn("w:fldCharType"), "begin")
        run_begin.append(fldChar_begin)

        run_instr = p.add_r()
        instrText = OxmlElement("w:instrText")
        instrText.set(qn("xml:space"), "preserve")
        instrText.text = 'TOC \\o "1-3" \\h \\z \\u'
        run_instr.append(instrText)

        run_sep = p.add_r()
        fldChar_sep = OxmlElement("w:fldChar")
        fldChar_sep.set(qn("w:fldCharType"), "separate")
        run_sep.append(fldChar_sep)

        run_text = p.add_r()
        t = OxmlElement("w:t")
        t.text = "Right-click and select 'Update Field' to generate Table of Contents."
        run_text.append(t)

        run_end = p.add_r()
        fldChar_end = OxmlElement("w:fldChar")
        fldChar_end.set(qn("w:fldCharType"), "end")
        run_end.append(fldChar_end)
