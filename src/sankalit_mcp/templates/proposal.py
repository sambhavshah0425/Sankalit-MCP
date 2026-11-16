from docx.shared import Pt
from sankalit_mcp.templates.base_template import BaseTemplate
from sankalit_mcp.templates.components.cover_page import (
    add_orange_rule,
    add_cover_logo,
    add_cover_title,
    add_project_details_table,
    add_document_control_table,
)


class ProposalTemplate(BaseTemplate):

    def generate(self, document, data, engine) -> None:
        """
        Generates a standard Proposal document layout.
        """
        engine.apply_document_defaults(document)

        # 1. Cover page
        add_orange_rule(document, engine)
        add_cover_logo(document, engine)
        add_cover_title(document, f"Proposal: {data.title}", engine)
        add_project_details_table(document, data, engine)
        add_document_control_table(document, data, engine)
        document.add_page_break()

        # 2. Proposal Sections
        if hasattr(data, "sections") and data.sections:
            for section in data.sections:
                p = document.add_paragraph()
                p.paragraph_format.space_before = Pt(18)
                p.paragraph_format.space_after = Pt(12)
                p.add_run(section.heading)
                engine.apply_heading(p, section.level)

                for line in section.text.split("\n"):
                    if line.strip():
                        p_body = document.add_paragraph(line)
                        engine.apply_body(p_body)
        else:
            # Executive Summary Section Fallback
            p1 = document.add_paragraph()
            p1.paragraph_format.space_before = Pt(18)
            p1.paragraph_format.space_after = Pt(12)
            run1 = p1.add_run("1. Executive Summary")
            engine.apply_heading(p1, 1)

            p1_body = document.add_paragraph(
                "This proposal outlines the design and consulting services offered by Sankalit Consultant."
            )
            engine.apply_body(p1_body)

            # Project Scope Section Fallback
            p2 = document.add_paragraph()
            p2.paragraph_format.space_before = Pt(18)
            p2.paragraph_format.space_after = Pt(12)
            run2 = p2.add_run("2. Project Scope")
            engine.apply_heading(p2, 1)

            p2_body = document.add_paragraph(
                "Detailed BIM modeling, airport departures systems integration, and DBR review services."
            )
            engine.apply_body(p2_body)
