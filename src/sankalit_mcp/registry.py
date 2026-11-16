from sankalit_mcp.handlers.txt import TXTHandler
from sankalit_mcp.handlers.md import MarkdownHandler
from sankalit_mcp.handlers.docx import DOCXHandler
from sankalit_mcp.handlers.pdf import PDFHandler


class HandlerRegistry:
    """Registry for document handlers."""

    def __init__(self):
        self._handlers = {
            ".txt": TXTHandler(),
            ".md": MarkdownHandler(),
            ".docx": DOCXHandler(),
            ".pdf": PDFHandler(),
        }

    def register(self, extension: str, handler):
        """Register a new handler."""
        self._handlers[extension.lower()] = handler

    def get_handler(self, extension: str):
        """Return the handler for a file extension."""

        extension = extension.lower()

        if extension not in self._handlers:
            raise ValueError(
                f"No handler registered for '{extension}'"
            )

        return self._handlers[extension]
