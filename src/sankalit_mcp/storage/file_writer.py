import hashlib
import mimetypes
from pathlib import Path
from typing import Optional


class FileWriter:

    @staticmethod
    def get_file_metadata(path: Path) -> dict:
        """
        Calculates and returns rich metadata for a file at path:
        size, sha256 hash, and mime_type.
        """
        if not path.exists():
            raise FileNotFoundError(f"File {path} does not exist.")

        size = path.stat().st_size

        # Calculate SHA-256
        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        sha256 = sha256_hash.hexdigest()

        # Guess mime type
        mime_type, _ = mimetypes.guess_type(path)
        if not mime_type:
            suffix = path.suffix.lower()
            if suffix == ".docx":
                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif suffix == ".pptx":
                mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            elif suffix == ".xlsx":
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif suffix == ".pdf":
                mime_type = "application/pdf"
            elif suffix == ".png":
                mime_type = "image/png"
            elif suffix == ".jpg" or suffix == ".jpeg":
                mime_type = "image/jpeg"
            elif suffix == ".md":
                mime_type = "text/markdown"
            elif suffix == ".txt":
                mime_type = "text/plain"
            else:
                mime_type = "application/octet-stream"

        return {
            "success": True,
            "path": str(path),
            "size": size,
            "sha256": sha256,
            "mime_type": mime_type,
        }

    @classmethod
    def write_text(
        cls,
        path: Path,
        content: str,
        overwrite: bool = False,
    ) -> dict:
        from sankalit_mcp.storage.text_writer import TextWriter
        return TextWriter.write(path, content, overwrite)

    @classmethod
    def write_binary(
        cls,
        path: Path,
        source_path: Optional[Path] = None,
        base64_content: Optional[str] = None,
        overwrite: bool = False,
    ) -> dict:
        from sankalit_mcp.storage.binary_writer import BinaryWriter
        return BinaryWriter.write(path, source_path, base64_content, overwrite)
