from docx.shared import Pt

from sankalit_mcp.templates.base_template import BaseTemplate
from sankalit_mcp.templates.components.cover_page import (
    add_orange_rule,
    add_cover_logo,
    add_cover_title,
    add_project_details_table,
    add_document_control_table,
    add_assumptions_box,
    add_callout_box,
)
from sankalit_mcp.templates.components.revision_table import (
    add_revision_history_table,
)
from sankalit_mcp.templates.components.abbreviations import (
    add_abbreviations_table,
)

# Recognized callout markers, matching the icon+label convention used in
# Sankalit reference manuals (e.g. "💡 Graduate Takeaway", "⚠️ Important",
# "🏗 Real Context — Dehradun Airport"). The icon is optional; the label
# text before an em-dash or line break is used as the callout title.
CALLOUT_ICONS = ("💡", "⚠️", "🏗", "📷")


class TechnicalReportTemplate(BaseTemplate):

    def generate(self, document, data, engine) -> None:
        """
        Generates the standard Technical Report structure.
        """
        # Apply page size, margins and fonts
        engine.apply_document_defaults(document, data)

        # 1. Cover page
        self._create_cover(document, data, engine)
        document.add_page_break()

        # 2. Front Matter (Revision History, Table of Contents, and Abbreviations flow naturally together on Page 2)
        generated_sections = []

        if hasattr(data, "revisions") and data.revisions:
            self._create_revision_history(document, data, engine)
            generated_sections.append("revision")

        show_toc = getattr(data, "show_toc", False)
        if show_toc:
            self._create_toc(document, data, engine)
            generated_sections.append("toc")

        if hasattr(data, "abbreviations") and data.abbreviations:
            self._create_abbreviations(document, data, engine)
            generated_sections.append("abbreviations")

        if "toc" in generated_sections:
            document.add_page_break()

        # 3. Report Body
        self._create_body(document, data, engine)

        # 4. Annexures
        if hasattr(data, "annexures") and data.annexures:
            document.add_page_break()
            self._create_annexures(document, data, engine)

    def _create_cover(self, doc, data, engine) -> None:
        add_orange_rule(doc, engine)
        add_cover_logo(doc, engine)
        add_cover_title(doc, data.title, engine)
        add_project_details_table(doc, data, engine)
        add_document_control_table(doc, data, engine)
        add_assumptions_box(doc, data.assumptions, engine)

    def _create_revision_history(self, doc, data, engine) -> None:
        add_revision_history_table(doc, data.revisions, engine)

    def _create_toc(self, doc, data, engine) -> None:
        p_hdr = doc.add_paragraph()
        p_hdr.paragraph_format.space_before = Pt(24)
        p_hdr.paragraph_format.space_after = Pt(12)
        run_hdr = p_hdr.add_run("Table of Contents")
        run_hdr.font.name = engine.get_style().fonts.font_family
        run_hdr.font.bold = True
        run_hdr.font.size = Pt(14)
        run_hdr.font.color.rgb = engine.hex_to_rgb(engine.get_style().typography.title.color)

        # Static TOC built from the known section list. A dynamic Word TOC
        # field only resolves when a human opens the file in Word and updates
        # fields manually — docx2pdf's headless conversion never triggers
        # that, so the field renders literally as its placeholder text.
        # Building it statically here guarantees correct output every time,
        # regardless of the conversion path.
        for section in data.sections:
            p_entry = doc.add_paragraph()
            p_entry.paragraph_format.space_after = Pt(4)
            indent = max(section.level - 1, 0) * Pt(12)
            p_entry.paragraph_format.left_indent = indent
            run_entry = p_entry.add_run(section.heading)
            run_entry.font.name = engine.get_style().fonts.font_family
            run_entry.font.size = Pt(11)

    def _create_abbreviations(self, doc, data, engine) -> None:
        add_abbreviations_table(doc, data.abbreviations, engine)

    def _create_body(self, doc, data, engine):
        for section in data.sections:
            p = doc.add_paragraph()
            engine.apply_heading(
                p,
                section.level
            )
            p.add_run(section.heading)

            for block in section.text.split("\n\n"):
                block = block.strip()
                if not block:
                    continue

                # Callout box (Graduate Takeaway / Important / Real Context)
                first_line, _, rest = block.partition("\n")
                stripped_first = first_line.strip()
                icon_found = next((i for i in CALLOUT_ICONS if stripped_first.startswith(i)), None)
                if icon_found:
                    label = stripped_first[len(icon_found):].strip()
                    body_text = rest.strip() or label
                    if rest.strip():
                        add_callout_box(doc, icon_found, label, body_text, engine)
                    else:
                        # Label and body were on the same line/only line — no separate body given
                        add_callout_box(doc, icon_found, "", body_text, engine)
                    continue

                # Bullet List
                if block.startswith(("-", "*", "•")):
                    for bullet in block.split("\n"):
                        bullet = bullet.lstrip("-*• ").strip()
                        para = doc.add_paragraph(
                            style="List Bullet"
                        )
                        para.add_run(bullet)
                        engine.apply_body(para)
                else:
                    para = doc.add_paragraph(block)
                    engine.apply_body(para)

    def _create_annexures(self, doc, data, engine) -> None:
        for idx, annexure_text in enumerate(data.annexures, 1):
            if idx > 1:
                doc.add_page_break()
            p_hdr = doc.add_paragraph()
            p_hdr.paragraph_format.space_before = Pt(24)
            p_hdr.paragraph_format.space_after = Pt(12)
            run_hdr = p_hdr.add_run(f"Annexure {idx}")
            engine.apply_heading(p_hdr, 1)

            for line in annexure_text.split("\n"):
                if line.strip():
                    p_body = doc.add_paragraph(line)
                    engine.apply_body(p_body)
