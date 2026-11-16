from docx.shared import Pt
from sankalit_mcp.templates.base_template import BaseTemplate
from sankalit_mcp.templates.components.cover_page import (
    add_orange_rule,
    add_cover_logo,
    add_cover_title,
)


class PresentationTemplate(BaseTemplate):

    def generate(self, document, data, engine) -> None:
        """
        Generates a standard Presentation document layout.
        """
        engine.apply_document_defaults(document)

        # 1. Title Slide
        add_orange_rule(document, engine)
        add_cover_logo(document, engine)
        add_cover_title(document, f"Presentation: {data.title}", engine)
        document.add_page_break()

        # 2. Agenda Slide
        p1 = document.add_paragraph()
        p1.paragraph_format.space_before = Pt(18)
        p1.paragraph_format.space_after = Pt(12)
        run1 = p1.add_run("Slide 1: Agenda")
        engine.apply_heading(p1, 1)

        p1_body = document.add_paragraph(
            "1. Introduction\n2. Design Scope & Standards\n3. Next Steps"
        )
        engine.apply_body(p1_body)
