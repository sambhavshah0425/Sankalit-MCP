from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_left_border(cell, fill_hex, sz="24"):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{fill_hex}"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)


def add_orange_rule(doc, engine) -> None:
    """Adds a thin orange rule spanning full content width."""
    table = doc.add_table(rows=1, cols=1)
    table.autofit = False
    table.columns[0].width = Inches(6.5)
    cell = table.cell(0, 0)
    set_cell_background(cell, "F5A623")  # Primary brand color
    # Make cell extremely short
    tr = table.rows[0]._tr
    trPr = tr.get_or_add_trPr()
    trHeight = parse_xml(f'<w:trHeight {nsdecls("w")} w:val="40" w:hRule="exact"/>')
    trPr.append(trHeight)


def add_cover_logo(doc, engine) -> None:
    """Adds a borderless table representing Variant 1 Logo on Left and Web on Right."""
    table = doc.add_table(rows=1, cols=2)
    table.autofit = False
    table.columns[0].width = Inches(4.5)
    table.columns[1].width = Inches(2.0)

    # Logo left cell
    cell_left = table.cell(0, 0)
    p_logo = cell_left.paragraphs[0]
    run_logo = p_logo.add_run("S A N K A L I T  C O N S U L T A N T")
    run_logo.font.name = engine.get_style().fonts.font_family
    run_logo.font.size = Pt(12)
    run_logo.font.bold = True
    run_logo.font.color.rgb = engine.hex_to_rgb(engine.get_style().typography.title.color)

    # Web right cell
    cell_right = table.cell(0, 1)
    p_web = cell_right.paragraphs[0]
    p_web.alignment = 2  # Right aligned
    run_web = p_web.add_run("www.sankalit.in")
    run_web.font.name = engine.get_style().fonts.font_family
    run_web.font.size = Pt(9)
    run_web.font.color.rgb = engine.hex_to_rgb(engine.get_style().typography.body.color)


def add_cover_title(doc, title_text: str, engine) -> None:
    """Adds standard 28pt Calibri Bold title."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(36)
    p.paragraph_format.space_after = Pt(24)
    run = p.add_run(title_text)
    run.font.name = engine.get_style().fonts.font_family
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = engine.hex_to_rgb(engine.get_style().typography.title.color)


def add_project_details_table(doc, data, engine) -> None:
    """Renders Client/Project/Location/Discipline as plain label-value
    lines, matching Sankalit's minimal house style (no table, no borders,
    no fill) — consistent with add_document_control_table below."""
    details = [
        ("Client", data.client),
        ("Project", data.project_name),
        ("Location", data.location),
        ("Discipline", data.discipline),
    ]
    details = [(label, val) for label, val in details if val]
    if not details:
        return

    for label, val in details:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        run_lbl = p.add_run(f"{label}:  ")
        run_lbl.font.name = engine.get_style().fonts.font_family
        run_lbl.font.bold = True
        run_lbl.font.size = Pt(10)
        run_lbl.font.color.rgb = engine.hex_to_rgb(engine.get_style().colors.charcoal)

        run_val = p.add_run(val)
        run_val.font.name = engine.get_style().fonts.font_family
        run_val.font.size = Pt(10)
        run_val.font.color.rgb = engine.hex_to_rgb(engine.get_style().typography.body.color)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)


def add_document_control_table(doc, data, engine) -> None:
    """Renders document control metadata as a plain dot-separated line,
    matching Sankalit's actual house style (no table, no fill, no borders)."""
    parts = [p for p in (data.doc_no, data.revision, data.date, data.classification) if p]
    if not parts:
        return

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(18)
    run = p.add_run(" · ".join(parts))
    run.font.name = engine.get_style().fonts.monospace_font
    run.font.size = Pt(9)
    run.font.color.rgb = engine.hex_to_rgb(engine.get_style().colors.charcoal)


def add_assumptions_box(doc, assumptions, engine) -> None:
    """Renders assumptions in an Orange-bordered callout box with light grey background."""
    if not assumptions:
        return

    p_hdr = doc.add_paragraph()
    p_hdr.paragraph_format.space_before = Pt(24)
    p_hdr.paragraph_format.space_after = Pt(6)
    run_hdr = p_hdr.add_run("Key Assumptions")
    run_hdr.font.name = engine.get_style().fonts.font_family
    run_hdr.font.bold = True
    run_hdr.font.size = Pt(12)
    run_hdr.font.color.rgb = engine.hex_to_rgb(engine.get_style().typography.title.color)

    # Callout single cell table
    table = doc.add_table(rows=1, cols=1)
    table.autofit = False
    table.columns[0].width = Inches(6.5)
    cell = table.cell(0, 0)

    # Styling callout background and borders
    set_cell_background(cell, "F5F5F5")  # Background Light Grey
    set_cell_left_border(cell, "F5A623", sz="36")  # Orange accent left border

    # Populate bullets
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(3)
    
    for idx, assumption in enumerate(assumptions):
        if idx > 0:
            p = cell.add_paragraph()
            p.paragraph_format.space_after = Pt(3)
        run_bullet = p.add_run("•  ")
        run_bullet.font.name = engine.get_style().fonts.font_family
        run_bullet.font.color.rgb = engine.hex_to_rgb(engine.get_style().typography.body.color)
        run_text = p.add_run(assumption)
        run_text.font.name = engine.get_style().fonts.font_family
        run_text.font.size = Pt(10)
        run_text.font.color.rgb = engine.hex_to_rgb(engine.get_style().typography.body.color)


def add_callout_box(doc, icon: str, label: str, text: str, engine) -> None:
    """
    Renders a callout box in the style used throughout Sankalit reference
    manuals — e.g. "Graduate Takeaway", "Important", "Real Context":
    light grey fill, orange left accent border, bold icon+label line
    followed by the body text.
    """
    table = doc.add_table(rows=1, cols=1)
    table.autofit = False
    table.columns[0].width = Inches(6.5)
    cell = table.cell(0, 0)

    set_cell_background(cell, "F5F5F5")  # Background Light Grey
    set_cell_left_border(cell, "F5A623", sz="36")  # Orange accent left border

    p_label = cell.paragraphs[0]
    p_label.paragraph_format.space_after = Pt(4)
    run_label = p_label.add_run(f"{icon}  {label}".strip())
    run_label.font.name = engine.get_style().fonts.font_family
    run_label.font.bold = True
    run_label.font.size = Pt(10)
    run_label.font.color.rgb = engine.hex_to_rgb(engine.get_style().colors.charcoal)

    p_body = cell.add_paragraph()
    p_body.paragraph_format.space_after = Pt(3)
    run_body = p_body.add_run(text)
    run_body.font.name = engine.get_style().fonts.font_family
    run_body.font.size = Pt(10)
    run_body.font.color.rgb = engine.hex_to_rgb(engine.get_style().typography.body.color)

    # Small spacer paragraph after the box so following body text doesn't
    # butt directly against it.
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
