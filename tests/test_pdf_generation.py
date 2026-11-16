import pytest
from pathlib import Path
from sankalit_mcp.services.document_service import DocumentService


def test_pdf_generation_e2e(tmp_path):
    output_pdf = tmp_path / "test_report.pdf"
    
    content = (
        "# Airport Terminal Expansion Study\n"
        "Project: Terminal 2 Expansion\n"
        "Client: Adani Airports\n"
        "Location: Mumbai, India\n"
        "Discipline: Airport Systems\n"
        "Prepared by: Sambhav Shah\n"
        "Reviewed by: Jigar Mehta\n"
        "Approved by: Jigar Mehta\n"
        "Revision: Rev 01\n"
        "Date: 23 July 2026\n"
        "Doc no: SKL-BIAL-DBR-001\n"
        "\n"
        "## 1. Introduction\n"
        "This study describes the integration requirements for the Terminal 2 expansion."
    )
    
    service = DocumentService()
    res = service.create(
        path=str(output_pdf),
        text_content=content,
        overwrite=True
    )
    
    assert res["success"] is True
    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0
    
    # Read the file's binary signature to verify it is a valid PDF
    with open(output_pdf, "rb") as f:
        header = f.read(5)
    assert header == b"%PDF-"


def test_invalid_document_type_raises():
    service = DocumentService()
    with pytest.raises(ValueError) as exc_info:
        service.create(
            path="test_invalid.docx",
            text_content="content",
            document_type="invalid_type",
            overwrite=True
        )
    assert "Invalid document_type" in str(exc_info.value)
