from pathlib import Path
from typing import Optional

from sankalit_mcp.storage.file_writer import FileWriter
from sankalit_mcp.utils.paths import resolve_path
from sankalit_mcp.utils.validation import validate_extension, validate_parent_exists


def write_binary_file(
    destination: str = "",
    source_path: Optional[str] = None,
    base64_content: Optional[str] = None,
    overwrite: bool = False,
    path: str = "",
):
    """
    Copies an existing binary file to the destination, or writes base64 decoded data.
    
    CRITICAL: Prefer using 'source_path' whenever the file already exists on disk (e.g., temporary PDFs, DOCX, or downloads).
    Only use 'base64_content' if the binary exists strictly in memory.
    
    Examples:
      - Copy file from disk:
        write_binary_file(source_path="/tmp/report.pdf", destination="Z:\\Airport Report.pdf")
      - Write base64 from memory:
        write_binary_file(base64_content="...", destination="Z:\\Airport Report.pdf")
    """
    dest = destination or path
    if not dest:
        raise ValueError("Either 'destination' or 'path' must be provided.")

    dest_path = resolve_path(dest)
    validate_extension(dest_path)
    validate_parent_exists(dest_path)

    src_p = resolve_path(source_path) if source_path else None

    return FileWriter.write_binary(
        path=dest_path,
        source_path=src_p,
        base64_content=base64_content,
        overwrite=overwrite,
    )
