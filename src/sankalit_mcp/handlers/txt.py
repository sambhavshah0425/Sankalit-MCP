from pathlib import Path

from sankalit_mcp.handlers.base import BaseHandler


class TXTHandler(BaseHandler):

    def write(
        self,
        path: Path,
        content: str,
        overwrite: bool = False,
    ) -> dict:
        from sankalit_mcp.storage.file_writer import FileWriter
        res = FileWriter.write_text(path, content, overwrite)
        res["message"] = "Text document created successfully."
        return res

    def read(
        self,
        path: Path,
    ) -> str:

        return path.read_text(
            encoding="utf-8"
        )
