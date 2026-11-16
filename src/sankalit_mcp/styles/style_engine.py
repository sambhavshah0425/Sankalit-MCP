from docx.shared import Mm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from sankalit_mcp.styles.sankalit_style import SankalitStyle
from sankalit_mcp.styles.style_config import StyleConfig


class StyleEngine:

    @staticmethod
    def hex_to_rgb(hex_str: str) -> RGBColor:
        h = hex_str.lstrip('#')
        return RGBColor(*(int(h[i:i+2], 16) for i in (0, 2, 4)))

    def __init__(self, style: StyleConfig | None = None):
        self.style = style or SankalitStyle.get()

    def get_style(self) -> StyleConfig:
        return self.style

    def apply_document_defaults(self, document, data=None) -> None:
        """
        Apply margins, default font face, size, and color to the document.
        `data` (BaseDocumentData) is optional but required to populate the
        brand-compliant header (project name, doc no/revision) and footer
        (page numbers) per Section 4.4.
        """
        # Apply margins to the first section
        if document.sections:
            section = document.sections[0]
            section.top_margin = Mm(self.style.document.margins["top"])
            section.bottom_margin = Mm(self.style.document.margins["bottom"])
            section.left_margin = Mm(self.style.document.margins["left"])
            section.right_margin = Mm(self.style.document.margins["right"])
            
            # Configure headers and footers
            section.different_first_page_header_footer = True
            self.apply_header(section, data)
            self.apply_footer(section)

        # Apply default fonts to the Normal style
        if "Normal" in document.styles:
            normal_style = document.styles["Normal"]
            font = normal_style.font
            font.name = self.style.fonts.font_family
            font.size = Pt(self.style.typography.body.size)
            font.color.rgb = self.hex_to_rgb(self.style.typography.body.color)

    # Section 3.3 spacing spec: (space_before_pt, space_after_pt) per heading level
    HEADING_SPACING = {
        1: (18, 12),
        2: (14, 8),
        3: (10, 6),
        4: (10, 6),
    }

    def apply_heading(self, paragraph, level: int) -> None:
        """
        Apply heading styles (H1-H4) based on level config, including the
        mandatory before/after spacing from Brand Guide Section 3.3.
        """
        document = paragraph.part.document
        style_name = f"Heading {level}"

        if style_name in document.styles:
            style = document.styles[style_name]
            font = style.font
            font.name = self.style.fonts.font_family

            if level == 1:
                cfg = self.style.typography.h1
            elif level == 2:
                cfg = self.style.typography.h2
            elif level == 3:
                cfg = self.style.typography.h3
            elif level == 4:
                cfg = self.style.typography.h4
            else:
                cfg = self.style.typography.body

            font.size = Pt(cfg.size)
            font.bold = cfg.bold
            font.italic = cfg.italic
            font.color.rgb = self.hex_to_rgb(cfg.color)

        paragraph.style = style_name

        before, after = self.HEADING_SPACING.get(level, (10, 6))
        paragraph.paragraph_format.space_before = Pt(before)
        paragraph.paragraph_format.space_after = Pt(after)

        # Spacing is applied but rule underline is removed per house style requirements

    def apply_body(self, paragraph) -> None:
        """
        Apply body text styling (Normal style) per Brand Guide Section 3.3:
        1.15x line spacing, 6pt space before/after, left alignment,
        no first-line indent.
        """
        paragraph.style = "Normal"
        pf = paragraph.paragraph_format
        pf.line_spacing = 1.15
        pf.space_before = Pt(6)
        pf.space_after = Pt(6)
        pf.first_line_indent = Pt(0)
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT

    def apply_table(self, table) -> None:
        """
        Apply default table grid styles.
        """
        table.style = "Table Grid"

    def _add_orange_rule(self, paragraph, position: str) -> None:
        """Adds a 1pt orange rule border (top or bottom) to a paragraph, per Section 4.4."""
        pPr = paragraph._p.get_or_add_pPr()
        pBdr = OxmlElement("w:pBdr")
        edge = OxmlElement(f"w:{position}")
        edge.set(qn("w:val"), "single")
        edge.set(qn("w:sz"), "8")  # ~1pt
        edge.set(qn("w:space"), "4")
        edge.set(qn("w:color"), "F5A623")  # Sankalit Orange
        pBdr.append(edge)
        pPr.append(pBdr)

    def apply_header(self, section, data=None) -> None:
        """
        Brand Guide Section 4.4 — Header, 3 zones via tab stops:
        Left: Sankalit wordmark (logo placeholder) | Centre: Project Name |
        Right: Doc No. | Revision (doc no in Consolas). Orange 1pt rule below.
        """
        header_p = section.header.paragraphs[0]
        header_p.text = ""
        header_p.style = "Normal"

        # Set centre/right tab stops across the usable page width (A4, 25/25mm margins ~ 6.93in usable)
        tab_stops = header_p.paragraph_format.tab_stops
        tab_stops.add_tab_stop(Pt(255), WD_TAB_ALIGNMENT.CENTER)
        tab_stops.add_tab_stop(Pt(510), WD_TAB_ALIGNMENT.RIGHT)

        project_name = getattr(data, "project_name", "") if data else ""
        doc_no = getattr(data, "doc_no", "") if data else ""
        revision = getattr(data, "revision", "") if data else ""

        run_logo = header_p.add_run("SANKALIT CONSULTANT")
        run_logo.font.name = self.style.fonts.font_family
        run_logo.font.size = Pt(8)
        run_logo.font.bold = True
        run_logo.font.color.rgb = self.hex_to_rgb(self.style.colors.charcoal)

        if project_name:
            header_p.add_run("\t")
            run_project = header_p.add_run(project_name)
            run_project.font.name = self.style.fonts.font_family
            run_project.font.size = Pt(8)
            run_project.font.color.rgb = self.hex_to_rgb(self.style.colors.charcoal)

        if doc_no or revision:
            if project_name:
                header_p.add_run("\t")
            else:
                header_p.add_run("\t\t")

            if doc_no and revision:
                run_docno = header_p.add_run(doc_no)
                run_docno.font.name = self.style.fonts.monospace_font
                run_docno.font.size = Pt(8)
                run_docno.font.color.rgb = self.hex_to_rgb(self.style.colors.charcoal)
                run_sep = header_p.add_run(" | ")
                run_sep.font.name = self.style.fonts.font_family
                run_sep.font.size = Pt(8)
                run_sep.font.color.rgb = self.hex_to_rgb(self.style.colors.charcoal)
                run_rev = header_p.add_run(revision)
                run_rev.font.name = self.style.fonts.font_family
                run_rev.font.size = Pt(8)
                run_rev.font.color.rgb = self.hex_to_rgb(self.style.colors.charcoal)
            elif doc_no:
                run_docno = header_p.add_run(doc_no)
                run_docno.font.name = self.style.fonts.monospace_font
                run_docno.font.size = Pt(8)
                run_docno.font.color.rgb = self.hex_to_rgb(self.style.colors.charcoal)
            else:
                run_rev = header_p.add_run(revision)
                run_rev.font.name = self.style.fonts.font_family
                run_rev.font.size = Pt(8)
                run_rev.font.color.rgb = self.hex_to_rgb(self.style.colors.charcoal)

        header_p.paragraph_format.space_after = Pt(6)
        self._add_orange_rule(header_p, "bottom")

    def apply_footer(self, section) -> None:
        """
        Brand Guide Section 4.4 — Footer, 3 zones:
        Left: blank | Centre: "Private & Confidential" (italic) |
        Right: "Page X of Y" (real Word field, not typed text).
        Orange 1pt rule above.
        """
        footer_p = section.footer.paragraphs[0]
        footer_p.text = ""
        footer_p.style = "Normal"

        tab_stops = footer_p.paragraph_format.tab_stops
        tab_stops.add_tab_stop(Pt(255), WD_TAB_ALIGNMENT.CENTER)
        tab_stops.add_tab_stop(Pt(510), WD_TAB_ALIGNMENT.RIGHT)

        footer_p.add_run("\t")
        run_conf = footer_p.add_run("Private & Confidential")
        run_conf.font.name = self.style.fonts.font_family
        run_conf.font.size = Pt(8)
        run_conf.font.italic = True
        run_conf.font.color.rgb = self.hex_to_rgb(self.style.colors.charcoal)

        footer_p.add_run("\t")
        run_page_label = footer_p.add_run("Page ")
        run_page_label.font.name = self.style.fonts.font_family
        run_page_label.font.size = Pt(8)
        run_page_label.font.color.rgb = self.hex_to_rgb(self.style.colors.charcoal)

        self._add_field(footer_p, "PAGE")

        run_of = footer_p.add_run(" of ")
        run_of.font.name = self.style.fonts.font_family
        run_of.font.size = Pt(8)
        run_of.font.color.rgb = self.hex_to_rgb(self.style.colors.charcoal)

        self._add_field(footer_p, "NUMPAGES")

        footer_p.paragraph_format.space_before = Pt(6)
        self._add_orange_rule(footer_p, "top")

    def _add_field(self, paragraph, field_code: str) -> None:
        """Inserts a real Word field (e.g. PAGE, NUMPAGES) that auto-updates on paginate/print."""
        run = paragraph.add_run()
        run.font.name = self.style.fonts.font_family
        run.font.size = Pt(8)
        run.font.color.rgb = self.hex_to_rgb(self.style.colors.charcoal)
        p = run._r

        fld_begin = OxmlElement("w:fldChar")
        fld_begin.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = f" {field_code} "
        fld_sep = OxmlElement("w:fldChar")
        fld_sep.set(qn("w:fldCharType"), "separate")
        fld_end = OxmlElement("w:fldChar")
        fld_end.set(qn("w:fldCharType"), "end")

        p.append(fld_begin)
        p.append(instr)
        p.append(fld_sep)
        p.append(fld_end)

    def apply_cover_page(self, document) -> None:
        """
        Apply standard cover page layout rules (Placeholder).
        """
        pass

    def apply_watermark(self, document) -> None:
        """
        Apply watermark text rules (Placeholder).
        """
        pass
