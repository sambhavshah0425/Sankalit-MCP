from pathlib import Path

from docx import Document

from sankalit_mcp.handlers.base import BaseHandler
from sankalit_mcp.styles.style_engine import StyleEngine


class DOCXHandler(BaseHandler):
    """Handler for Microsoft Word (.docx) documents."""

    def write(
        self,
        path: Path,
        content: str,
        overwrite: bool = False,
    ) -> dict:

        if path.exists() and not overwrite:
            raise FileExistsError(
                f"{path} already exists."
            )

        document = Document()
        engine = StyleEngine()
        engine.apply_document_defaults(document)

        # Split into paragraphs and format accordingly
        for paragraph in content.split("\n"):
            p_text = paragraph.strip()
            if p_text.startswith("# "):
                p = document.add_paragraph(p_text[2:])
                engine.apply_heading(p, 1)
            elif p_text.startswith("## "):
                p = document.add_paragraph(p_text[3:])
                engine.apply_heading(p, 2)
            elif p_text.startswith("### "):
                p = document.add_paragraph(p_text[4:])
                engine.apply_heading(p, 3)
            else:
                p = document.add_paragraph(paragraph)
                engine.apply_body(p)

        document.save(path)
        from sankalit_mcp.storage.file_writer import FileWriter
        res = FileWriter.get_file_metadata(path)
        res["message"] = "DOCX document created successfully."
        return res

    def write_document(
        self,
        path: Path,
        document: Document,
        overwrite: bool = False,
    ) -> dict:
        if path.exists() and not overwrite:
            raise FileExistsError(
                f"{path} already exists."
            )
        document.save(path)
        from sankalit_mcp.storage.file_writer import FileWriter
        res = FileWriter.get_file_metadata(path)
        res["message"] = "DOCX document created successfully."
        return res

    def read(
        self,
        path: Path,
    ) -> str:

        document = Document(path)

        paragraphs = []

        for paragraph in document.paragraphs:
            paragraphs.append(paragraph.text)

        return "\n".join(paragraphs)
