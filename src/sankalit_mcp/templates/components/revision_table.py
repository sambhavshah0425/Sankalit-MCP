from docx.shared import Pt, Inches
from sankalit_mcp.templates.components.cover_page import set_cell_background


def add_revision_history_table(doc, revisions, engine) -> None:
    """Renders the standard Revision History section and grid."""
    p_hdr = doc.add_paragraph()
    p_hdr.paragraph_format.space_before = Pt(24)
    p_hdr.paragraph_format.space_after = Pt(12)
    run_hdr = p_hdr.add_run("Revision History")
    run_hdr.font.name = engine.get_style().fonts.font_family
    run_hdr.font.bold = True
    run_hdr.font.size = Pt(14)
    run_hdr.font.color.rgb = engine.hex_to_rgb(engine.get_style().typography.title.color)

    if not revisions:
        p_empty = doc.add_paragraph("No revisions recorded.")
        p_empty.paragraph_format.space_after = Pt(12)
        return

    table = doc.add_table(rows=len(revisions) + 1, cols=4)
    table.style = "Table Grid"
    table.autofit = False
    table.columns[0].width = Inches(1.0)
    table.columns[1].width = Inches(1.5)
    table.columns[2].width = Inches(1.5)
    table.columns[3].width = Inches(2.5)

    # Renders headers
    headers = ["Rev", "Date", "Prepared By", "Summary of Changes"]
    for col_idx, text in enumerate(headers):
        cell = table.cell(0, col_idx)
        p = cell.paragraphs[0]
        run = p.add_run(text)
        run.font.name = engine.get_style().fonts.font_family
        run.font.bold = True
        run.font.size = Pt(10)
        set_cell_background(cell, "5A5A5A")  # Charcoal Header
        run.font.color.rgb = engine.hex_to_rgb(engine.get_style().colors.white)

    # Renders data rows
    for row_idx, rev_info in enumerate(revisions, 1):
        values = [rev_info.rev, rev_info.date, rev_info.prepared_by, rev_info.description]
        for col_idx, val in enumerate(values):
            cell = table.cell(row_idx, col_idx)
            p = cell.paragraphs[0]
            run = p.add_run(val)
            run.font.name = engine.get_style().fonts.font_family
            run.font.size = Pt(10)
            run.font.color.rgb = engine.hex_to_rgb(engine.get_style().typography.body.color)
            
            # Alternating row highlights
            if engine.get_style().tables.alternating_rows and row_idx % 2 == 0:
                set_cell_background(cell, "F5F5F5")  # Light Grey fill
