from docx.shared import Pt
from sankalit_mcp.templates.base_template import BaseTemplate
from sankalit_mcp.templates.components.cover_page import (
    add_orange_rule,
    add_cover_logo,
    add_cover_title,
    add_project_details_table,
)


class MeetingMinutesTemplate(BaseTemplate):

    def generate(self, document, data, engine) -> None:
        """
        Generates a standard Meeting Minutes layout.
        """
        engine.apply_document_defaults(document)

        # 1. Header rules and logo title
        add_orange_rule(document, engine)
        add_cover_logo(document, engine)
        add_cover_title(document, f"Meeting Minutes - {data.title}", engine)
        add_project_details_table(document, data, engine)
        document.add_page_break()

        # 2. Attendees Section
        p1 = document.add_paragraph()
        p1.paragraph_format.space_before = Pt(18)
        p1.paragraph_format.space_after = Pt(12)
        run1 = p1.add_run("1. Attendees")
        engine.apply_heading(p1, 1)

        p1_body = document.add_paragraph(
            f"Meeting chaired by {data.prepared_by}. Reviewers: {data.reviewed_by}."
        )
        engine.apply_body(p1_body)

        # 3. Discussion Points Section
        p2 = document.add_paragraph()
        p2.paragraph_format.space_before = Pt(18)
        p2.paragraph_format.space_after = Pt(12)
        run2 = p2.add_run("2. Discussion Points")
        engine.apply_heading(p2, 1)

        p2_body = document.add_paragraph(
            "Reviewed initial draft layout. Action items have been compiled below."
        )
        engine.apply_body(p2_body)
