import pytest
from pathlib import Path
from reportlab.pdfgen import canvas
from sankalit_mcp.handlers.pdf import PDFHandler, clean_text
from sankalit_mcp.services.document_service import DocumentService


def test_clean_text():
    text = "Hello\r world!\n\n\nThis is a    test.\n\n\n\nNewline."
    cleaned = clean_text(text)
    assert cleaned == "Hello world!\n\nThis is a test.\n\nNewline."


def test_pdf_handler_read(tmp_path):
    pdf_path = tmp_path / "test_doc.pdf"
    
    # Generate a simple PDF
    c = canvas.Canvas(str(pdf_path))
    c.drawString(100, 750, "Hello World from PDF Reader!")
    c.save()
    
    handler = PDFHandler()
    extracted_text = handler.read(pdf_path)
    
    assert "Hello World from PDF Reader!" in extracted_text


def test_pdf_handler_write_raises():
    handler = PDFHandler()
    with pytest.raises(NotImplementedError) as exc_info:
        handler.write(Path("test.pdf"), "content")
    assert "PDFHandler supports reading only." in str(exc_info.value)


def test_document_service_pdf_integration(tmp_path):
    pdf_path = tmp_path / "test_doc_integration.pdf"
    
    # Generate simple PDF
    c = canvas.Canvas(str(pdf_path))
    c.drawString(100, 750, "Integrated PDF service reading test.")
    c.save()
    
    service = DocumentService()
    extracted_text = service.read(str(pdf_path))
    
    assert "Integrated PDF service reading test." in extracted_text
