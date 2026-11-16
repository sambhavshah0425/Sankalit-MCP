import re
from pathlib import Path
from pypdf import PdfReader

from sankalit_mcp.handlers.base import BaseHandler


def clean_text(text: str) -> str:
    text = text.replace("\r", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class PDFHandler(BaseHandler):
    """
    Reads text from PDF documents.
    """

    def write(self, *args, **kwargs) -> dict:
        raise NotImplementedError(
            "PDFHandler supports reading only. PDF generation is handled by the document generation pipeline."
        )

    def read(self, path: Path) -> str:
        path = Path(path)
        reader = PdfReader(path)
        pages = []

        for page in reader.pages:
            try:
                text = page.extract_text() or ""
                pages.append(text)
            except Exception:
                pages.append("")

        return clean_text("\n\n".join(pages))
