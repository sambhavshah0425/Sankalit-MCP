import pytest
from pathlib import Path
from docx import Document

from sankalit_mcp.services.document_service import DocumentService
from sankalit_mcp.config import ROOT_DIRECTORY


@pytest.mark.parametrize(
    "filename, template_name, content, expected_texts",
    [
        (
            "test_tech_report.docx",
            "technical_report",
            "# Airport Systems Integration Study\nProject: Terminal expansion\n## 1. Introduction\nBody text content.",
            ["Airport Systems Integration Study", "Rev 00", "1. Introduction"]
        ),
        (
            "test_proposal.docx",
            "proposal",
            "# Metro Line Proposal\nProject: Metro Line 3\n## 1. Executive Summary\nProposal scope details.\n## 2. Project Scope\nProject scope details.",
            ["Proposal: Metro Line Proposal", "Rev 00", "1. Executive Summary", "2. Project Scope"]
        ),
        (
            "test_meeting_minutes.docx",
            "meeting_minutes",
            "# Weekly Alignment Meeting\nProject: Runway design\n## 1. Attendees\nAttendees lists go here, listing all project participants and stakeholders present during this weekly review alignment session.",
            ["Meeting Minutes - Weekly Alignment Meeting", "Attendees", "2. Discussion Points"]
        ),
        (
            "test_presentation.docx",
            "presentation",
            "# Final Pitch Slides\nProject: Airport tender\n## Slide 1: Agenda\nAgenda points details including introductions, scope review, timeline details, and commercial proposal summaries.",
            ["Presentation: Final Pitch Slides", "Slide 1: Agenda"]
        ),
    ],
)
def test_template_pipeline_e2e(filename, template_name, content, expected_texts):
    doc_service = DocumentService()
    
    # 1. Generate document via pipeline
    res = doc_service.create(filename, content, overwrite=True)
    assert res["success"] is True
    
    saved_path = Path(res["path"])
    assert saved_path.exists()
    
    try:
        # 2. Open and inspect
        doc = Document(saved_path)
        
        # 3. Assertions
        assert len(doc.paragraphs) > 0
        
        all_text = "\n".join(p.text for p in doc.paragraphs)
        assert any(p.text.strip() for p in doc.paragraphs)
        
        # Verify specific expected layout strings
        for expected_text in expected_texts:
            assert expected_text in all_text
            
    finally:
        # Cleanup
        saved_path.unlink(missing_ok=True)


def generate_document(template_name: str) -> Path:
    doc_service = DocumentService()
    filename = f"test_temp_{template_name}.docx"
    
    content_map = {
        "technical_report": "# Airport Systems Integration Study\nProject: Terminal expansion\n## 1. Introduction\nBody text content.",
        "proposal": "# Metro Line Proposal\nProject: Metro Line 3\n## 1. Executive Summary\nProposal scope details go here, outlining the entire route plan, feasibility studies, and financial budgets for the metro corridor.",
        "meeting_minutes": "# Weekly Alignment Meeting\nProject: Runway design\n## 1. Attendees\nAttendees lists go here, listing all project participants and stakeholders present during this weekly review alignment session.",
        "presentation": "# Final Pitch Slides\nProject: Airport tender\n## Slide 1: Agenda\nAgenda points details including introductions, scope review, timeline details, and commercial proposal summaries.",
    }
    
    content = content_map.get(template_name, "Some generic content")
    res = doc_service.create(filename, content, overwrite=True)
    assert res["success"] is True
    return Path(res["path"])


@pytest.mark.parametrize(
    "template_name",
    [
        "technical_report",
        "proposal",
        "meeting_minutes",
        "presentation",
    ],
)
def test_template_generates_non_empty_document(template_name):
    path = generate_document(template_name)
    try:
        doc = Document(path)

        assert len(doc.paragraphs) > 0
        assert any(p.text.strip() for p in doc.paragraphs)

        # Regression test: ensure no internal branding instructions leak into document body text
        text = "\n".join(p.text for p in doc.paragraphs)
        assert "Sankalit Document Branding Instructions" not in text
        assert "Typography" not in text
        assert "Brand Colors" not in text
        assert "Page Layout" not in text
    finally:
        path.unlink(missing_ok=True)


def test_create_structured_content_e2e():
    doc_service = DocumentService()
    
    def get_doc_text(doc):
        texts = [para.text for para in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    texts.append(cell.text)
        return "\n".join(texts)

    # 1. Technical Report
    tech_data = {
        "title": "Structured Tech Report",
        "project_name": "Hyperloop Link",
        "client": "Virgin",
        "location": "Nevada, USA",
        "discipline": "Tunnel Systems",
        "prepared_by": "Sambhav Shah",
        "reviewed_by": "Jigar Mehta",
        "approved_by": "Jigar Mehta",
        "revision": "Rev 01",
        "date": "22 July 2026",
        "doc_no": "SKL-HYP-001",
        "assumptions": ["Assum 1", "Assum 2"],
        "revisions": [
            {"rev": "Rev 00", "date": "21 July 2026", "prepared_by": "Sambhav", "description": "Draft"},
            {"rev": "Rev 01", "date": "22 July 2026", "prepared_by": "Sambhav", "description": "Final"}
        ],
        "abbreviations": [
            {"term": "TOC", "definition": "Table of Contents"}
        ],
        "sections": [
            {"heading": "1. Scope", "text": "Scope of hyperloop tunneling.", "level": 1},
            {"heading": "1.1 Details", "text": "Details of the route.", "level": 2}
        ],
        "annexures": ["Annex A text"]
    }
    
    res = doc_service.create(
        path="test_struct_tech.docx",
        structured_content=tech_data,
        document_type="technical_report",
        overwrite=True
    )
    assert res["success"] is True
    assert res["size"] > 0
    assert "sha256" in res
    assert res["mime_type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    p = Path(res["path"])
    try:
        doc = Document(p)
        all_text = get_doc_text(doc)
        assert "Structured Tech Report" in all_text
        assert "Hyperloop Link" in all_text
        assert "1. Scope" in all_text
        assert "1.1 Details" in all_text
    finally:
        p.unlink(missing_ok=True)

    # 2. Proposal
    prop_data = {
        "title": "Structured Proposal",
        "sections": [
            {"heading": "1. Pitch", "text": "Proposal details here.", "level": 1}
        ]
    }
    res = doc_service.create(
        path="test_struct_prop.docx",
        structured_content=prop_data,
        document_type="proposal",
        overwrite=True
    )
    assert res["success"] is True
    p = Path(res["path"])
    try:
        doc = Document(p)
        all_text = get_doc_text(doc)
        assert "Proposal: Structured Proposal" in all_text
        assert "1. Pitch" in all_text
    finally:
        p.unlink(missing_ok=True)

    # 3. Meeting Minutes
    mm_data = {
        "title": "Structured MOM",
        "attendees": ["Alice", "Bob"],
        "discussion_points": ["Point A", "Point B"]
    }
    res = doc_service.create(
        path="test_struct_mom.docx",
        structured_content=mm_data,
        document_type="meeting_minutes",
        overwrite=True
    )
    assert res["success"] is True
    p = Path(res["path"])
    try:
        doc = Document(p)
        all_text = get_doc_text(doc)
        assert "Meeting Minutes - Structured MOM" in all_text
    finally:
        p.unlink(missing_ok=True)

    # 4. Presentation
    pres_data = {
        "title": "Structured Slides",
        "slides": [{"title": "Agenda", "bullet": "Intro"}]
    }
    res = doc_service.create(
        path="test_struct_pres.docx",
        structured_content=pres_data,
        document_type="presentation",
        overwrite=True
    )
    assert res["success"] is True
    p = Path(res["path"])
    try:
        doc = Document(p)
        all_text = get_doc_text(doc)
        assert "Presentation: Structured Slides" in all_text
    finally:
        p.unlink(missing_ok=True)



def test_write_binary_file_tool():
    from sankalit_mcp.tools.write_binary_file import write_binary_file
    import base64
    
    # 1. Base64 write of a dummy txt
    dummy_text = "Hello Binary World!"
    b64_data = base64.b64encode(dummy_text.encode("utf-8")).decode("utf-8")
    
    res = write_binary_file(
        destination="test_binary_base64.txt",
        base64_content=b64_data,
        overwrite=True
    )
    assert res["success"] is True
    assert res["size"] == len(dummy_text)
    assert "sha256" in res
    assert res["mime_type"] == "text/plain"
    
    p = Path(res["path"])
    try:
        assert p.read_text(encoding="utf-8") == dummy_text
    finally:
        p.unlink(missing_ok=True)

    # 2. Copy source_path write of a dummy docx
    doc_service = DocumentService()
    res_docx = doc_service.create(
        "temp_source.docx",
        "Dummy docx content to satisfy the new content length verification check in DocumentService create, ensuring it is at least one hundred characters long.",
        overwrite=True
    )
    src_path = res_docx["path"]
    
    res_copy = write_binary_file(
        destination="test_binary_copied.docx",
        source_path=src_path,
        overwrite=True
    )
    assert res_copy["success"] is True
    assert res_copy["size"] == res_docx["size"]
    assert res_copy["sha256"] == res_docx["sha256"]
    assert res_copy["mime_type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    dest_path = Path(res_copy["path"])
    try:
        assert dest_path.exists()
    finally:
        dest_path.unlink(missing_ok=True)
        Path(src_path).unlink(missing_ok=True)


def test_from_text_orphan_lines_captured():
    from sankalit_mcp.templates.models import TechnicalReportData
    
    content = "This is some orphan text appearing before any Markdown heading.\nIt has multiple lines.\n## Section 1\nSection 1 content."
    data = TechnicalReportData.from_text(content)
    
    assert len(data.sections) == 2
    assert data.sections[0].heading == "Introduction"
    assert "orphan text" in data.sections[0].text
    assert "multiple lines" in data.sections[0].text
    assert data.sections[1].heading == "Section 1"
    assert data.sections[1].text == "Section 1 content."
    assert len(data.parse_warnings) > 0
    assert any("Orphan text" in w for w in data.parse_warnings)


def test_from_text_no_orphan_lines():
    from sankalit_mcp.templates.models import TechnicalReportData
    
    content = "## Section 1\nSection 1 content."
    data = TechnicalReportData.from_text(content)
    
    assert len(data.sections) == 1
    assert data.sections[0].heading == "Section 1"
    assert len(data.parse_warnings) == 0


def test_short_but_real_content_passes():
    from sankalit_mcp.services.document_service import DocumentService
    doc_service = DocumentService()
    res = doc_service.create(
        path="test_short_real.docx",
        text_content="## Intro\nThis is a short report.",
        overwrite=True
    )
    assert res["success"] is True
    Path(res["path"]).unlink(missing_ok=True)


def test_empty_content_rejected():
    from sankalit_mcp.services.document_service import DocumentService
    doc_service = DocumentService()
    with pytest.raises(ValueError) as exc_info:
        doc_service.create(
            path="test_empty.docx",
            text_content="   \n   ",
            overwrite=True
        )
    assert "The report content is empty." in str(exc_info.value)


def test_structured_meeting_minutes_guard_passes():
    from sankalit_mcp.services.document_service import DocumentService
    doc_service = DocumentService()
    res = doc_service.create(
        path="test_struct_mm.docx",
        structured_content={
            "title": "Short Minutes",
            "attendees": ["Alice", "Bob"],
            "discussion_points": ["Review pipeline status"]
        },
        document_type="meeting_minutes",
        overwrite=True
    )
    assert res["success"] is True
    Path(res["path"]).unlink(missing_ok=True)


def test_structured_meeting_minutes_guard_fails():
    from sankalit_mcp.services.document_service import DocumentService
    doc_service = DocumentService()
    with pytest.raises(ValueError) as exc_info:
        doc_service.create(
            path="test_struct_mm_fail.docx",
            structured_content={
                "title": "Empty Minutes",
                "attendees": [],
                "discussion_points": []
            },
            document_type="meeting_minutes",
            overwrite=True
        )
    assert "The report content is empty." in str(exc_info.value)


def test_resolve_path_sandboxing():
    from sankalit_mcp.utils.paths import resolve_path
    from sankalit_mcp import config
    import pytest
    
    # Paths inside workspace should resolve fine
    resolved = resolve_path("test_inside.docx")
    assert resolved.name == "test_inside.docx"
    
    # Paths outside WORKSPACE_ROOT should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        resolve_path("C:/Users/Sambhav/Documents/some_other_folder/test.docx")
    assert "Access denied" in str(exc_info.value)


def test_config_workspace_root_fallback(monkeypatch):
    import importlib
    import os
    import sankalit_mcp.config
    
    # Simulate being in Windows System32 directory
    monkeypatch.setenv("SANKALIT_WORKSPACE", "")
    monkeypatch.setattr(os, "getcwd", lambda: "C:\\Windows\\System32")
    
    # Reload config to apply mock environment
    importlib.reload(sankalit_mcp.config)
    
    # It should fall back to PROJECT_ROOT
    assert sankalit_mcp.config.WORKSPACE_ROOT == sankalit_mcp.config.PROJECT_ROOT
    
    # Cleanup config state
    importlib.reload(sankalit_mcp.config)


def test_config_workspace_roots_parsing(monkeypatch):
    import importlib
    import sankalit_mcp.config as cfg

    # 1. A single UNC root is parsed into one canonical root.
    monkeypatch.setenv("SANKALIT_WORKSPACE", "\\\\host\\Sales")
    importlib.reload(cfg)
    assert cfg.WORKSPACE_ROOT == cfg.canonicalize("\\\\host\\Sales")
    assert cfg.WORKSPACE_ROOTS == [cfg.canonicalize("\\\\host\\Sales")]

    # 2. Multiple semicolon-separated roots are all captured.
    monkeypatch.setenv("SANKALIT_WORKSPACE", "\\\\host\\Sales;\\\\host\\Marketing")
    importlib.reload(cfg)
    assert len(cfg.WORKSPACE_ROOTS) == 2
    assert cfg.canonicalize("\\\\host\\Sales") in cfg.WORKSPACE_ROOTS
    assert cfg.canonicalize("\\\\host\\Marketing") in cfg.WORKSPACE_ROOTS
    # The primary root is the first one listed.
    assert cfg.WORKSPACE_ROOT == cfg.canonicalize("\\\\host\\Sales")

    # Cleanup config state
    monkeypatch.delenv("SANKALIT_WORKSPACE", raising=False)
    importlib.reload(cfg)


def test_resolve_path_sandboxing_z_drive(monkeypatch):
    from sankalit_mcp.utils.paths import resolve_path
    import sankalit_mcp.config
    import pytest
    
    # Temporarily set workspace root to Z:\
    monkeypatch.setattr(sankalit_mcp.config, "WORKSPACE_ROOT", Path("Z:\\").resolve())
    
    # Z:\Sambhav\Test.docx should work
    resolved = resolve_path("Z:\\Sambhav\\Test.docx")
    assert resolved == Path("Z:\\Sambhav\\Test.docx").resolve()
    
    # Z:\Projects\Report.pdf should work
    resolved = resolve_path("Z:\\Projects\\Report.pdf")
    assert resolved == Path("Z:\\Projects\\Report.pdf").resolve()
    
    # E:\ should be rejected
    with pytest.raises(ValueError) as exc_info:
        resolve_path("E:\\test.docx")
    assert "Access denied" in str(exc_info.value)
    
    # C:\Users should be rejected
    with pytest.raises(ValueError) as exc_info:
        resolve_path("C:\\Users\\test.docx")
    assert "Access denied" in str(exc_info.value)


def test_multi_root_sandboxing(monkeypatch):
    from sankalit_mcp.utils.paths import resolve_path
    import sankalit_mcp.config

    # Use UNC roots so the test does not depend on this machine's drive letters.
    root_a = sankalit_mcp.config.canonicalize("\\\\host\\Sales")
    root_b = sankalit_mcp.config.canonicalize("\\\\host\\Marketing")
    monkeypatch.setattr(sankalit_mcp.config, "WORKSPACE_ROOTS", [root_a, root_b])
    monkeypatch.setattr(sankalit_mcp.config, "WORKSPACE_ROOT", root_a)

    # Deeply nested paths inside either root are allowed.
    deep = resolve_path("\\\\host\\Sales\\10. Proposal\\a\\b\\c\\d\\file.pdf")
    assert deep.relative_to(root_a) == Path("10. Proposal/a/b/c/d/file.pdf")
    assert resolve_path("\\\\host\\Marketing\\deck.pptx").relative_to(root_b) == \
        Path("deck.pptx")

    # A path outside all roots is denied.
    with pytest.raises(ValueError) as exc_info:
        resolve_path("\\\\host\\StandardData\\file.txt")
    assert "Access denied" in str(exc_info.value)


def test_drive_map_translation(monkeypatch):
    import importlib
    import sankalit_mcp.config
    from sankalit_mcp.utils.paths import resolve_path

    # Map Z: -> the UNC share, and allow that UNC share as the workspace root.
    monkeypatch.setenv("SANKALIT_DRIVE_MAP", "Z=\\\\192.168.1.5\\Sales")
    monkeypatch.setenv("SANKALIT_WORKSPACE", "\\\\192.168.1.5\\Sales")
    importlib.reload(sankalit_mcp.config)

    try:
        # A mapped-drive path is translated to UNC and accepted.
        resolved = resolve_path("Z:\\10. Proposal\\Edge\\ICT\\Rev 1\\file.pdf")
        assert str(resolved).replace("/", "\\") == \
            "\\\\192.168.1.5\\Sales\\10. Proposal\\Edge\\ICT\\Rev 1\\file.pdf"

        # The equivalent UNC path resolves the same and is accepted too.
        resolved_unc = resolve_path("\\\\192.168.1.5\\Sales\\10. Proposal\\file.pdf")
        assert "Sales" in str(resolved_unc)
    finally:
        monkeypatch.delenv("SANKALIT_DRIVE_MAP", raising=False)
        monkeypatch.delenv("SANKALIT_WORKSPACE", raising=False)
        importlib.reload(sankalit_mcp.config)


def test_pdf_conversion_timeout(monkeypatch):
    import time
    from pathlib import Path
    import pytest
    from sankalit_mcp.services.template_service import _convert_with_timeout

    def mock_convert(src, dest):
        time.sleep(2)

    import docx2pdf
    monkeypatch.setattr(docx2pdf, "convert", mock_convert)

    with pytest.raises(TimeoutError) as exc_info:
        _convert_with_timeout(Path("dummy_src.docx"), Path("dummy_dest.pdf"), timeout_s=1)
    
    assert "docx2pdf conversion exceeded 1s" in str(exc_info.value)


def test_document_generation_empty_metadata(tmp_path):
    from sankalit_mcp.services.document_service import DocumentService
    from docx import Document
    
    doc_service = DocumentService()
    dest_path = tmp_path / "test_empty_metadata.docx"
    
    structured_data = {
        "title": "Minimal Title",
        # Empty client/project_name to test conditional cover block omission
        "client": "",
        "project_name": "",
        "sections": [
            {"heading": "1. Scope", "text": "This is sample scope details of the test document.", "level": 1}
        ]
    }
    
    res = doc_service.create(
        path=str(dest_path),
        structured_content=structured_data,
        document_type="technical_report",
        overwrite=True
    )
    
    assert res["success"] is True
    assert dest_path.exists()
    
    doc = Document(dest_path)
    
    # Verify that the title is present in core properties or paragraph text
    all_text = "\n".join(p.text for p in doc.paragraphs)
    assert "Minimal Title" in all_text
    
    # If client and project name are empty, we should not have "Client:" or "Project Name:" anywhere
    assert "Client:" not in all_text
    assert "Project Name:" not in all_text
    
    # Ensure tables in doc do not contain "Client:" or "Project Name:"
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                assert "Client:" not in cell.text
                assert "Project Name:" not in cell.text

    # Verify tables:
    # 1. Logo table (cols=2)
    # 2. Orange rule table (cols=1)
    # No more bordered grids for details or document control.
    assert len(doc.tables) == 2
    
    # Verify metadata elements are present in plain text (dot-separated)
    assert "Rev 00" in all_text
    assert "Private & Confidential" in all_text
    assert "· Rev 00 ·" in all_text or "Rev 00 ·" in all_text or "· Rev 00" in all_text


def test_heading_rule_and_title_duplication_and_toc_threshold(tmp_path):
    from sankalit_mcp.services.document_service import DocumentService
    from docx import Document
    
    # 1. Test from_text parsing for title duplication
    doc_service = DocumentService()
    content = (
        "# Document Title Heading\n"
        "Project: Test Project\n"
        "## 1. First Section\n"
        "Text of first section.\n"
        "## 2. Second Section\n"
        "Text of second section.\n"
        "## 3. Third Section\n"
        "Text.\n"
        "## 4. Fourth Section\n"
        "Text.\n"
        "## 5. Fifth Section\n"
        "Text.\n"
        "## 6. Sixth Section\n"
        "Text.\n"
        "## 7. Seventh Section\n"
        "Text.\n"
        "## 8. Eighth Section\n"
        "Text.\n"
        "## 9. Ninth Section\n"
        "Text.\n"
        "## 10. Tenth Section\n"
        "Text.\n"
    )
    
    # Verify title duplication check in from_text parsing directly
    from sankalit_mcp.templates.models import TechnicalReportData
    parsed_data = TechnicalReportData.from_text(content)
    assert parsed_data.title == "Document Title Heading"
    # The first heading should be title, and should not be a section.
    # Total sections should be 10.
    assert len(parsed_data.sections) == 10
    assert parsed_data.sections[0].heading == "1. First Section"
    
    # 2. Verify TOC is NOT generated for 10 sections by default
    dest_no_toc = tmp_path / "no_toc.docx"
    res_no_toc = doc_service.create(
        path=str(dest_no_toc),
        content=content,
        document_type="technical_report",
        overwrite=True
    )
    assert res_no_toc["success"] is True
    doc_no_toc = Document(dest_no_toc)
    all_text_no_toc = "\n".join(p.text for p in doc_no_toc.paragraphs)
    assert "Table of Contents" not in all_text_no_toc

    # Helper to count manual page breaks
    def count_page_breaks(doc):
        count = 0
        for p in doc.paragraphs:
            for r in p.runs:
                for br in r._r.br_lst:
                    if br.type == "page":
                        count += 1
        return count

    # Since TOC is not generated, we should only have 1 page break (from cover page)
    assert count_page_breaks(doc_no_toc) == 1
    
    # 3. Verify TOC IS generated when show_toc is explicitly True (using structured content)
    dest_with_toc = tmp_path / "with_toc.docx"
    structured_data = {
        "title": "Document Title Heading",
        "show_toc": True,
        "sections": [
            {"heading": f"Section {i}", "text": "Text.", "level": 1}
            for i in range(1, 11)
        ]
    }
    res_with_toc = doc_service.create(
        path=str(dest_with_toc),
        structured_content=structured_data,
        document_type="technical_report",
        overwrite=True
    )
    assert res_with_toc["success"] is True
    doc_with_toc = Document(dest_with_toc)
    all_text_with_toc = "\n".join(p.text for p in doc_with_toc.paragraphs)
    assert "Table of Contents" in all_text_with_toc
    
    # Since TOC is generated, we should have exactly 2 page breaks (after cover and after TOC)
    assert count_page_breaks(doc_with_toc) == 2



