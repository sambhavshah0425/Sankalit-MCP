import base64
from pathlib import Path
import shutil
from typing import Optional


class BinaryWriter:

    @staticmethod
    def write(
        path: Path,
        source_path: Optional[Path] = None,
        base64_content: Optional[str] = None,
        overwrite: bool = False,
    ) -> dict:
        if path.exists() and not overwrite:
            raise FileExistsError(f"Destination file {path} already exists.")

        if source_path:
            if not source_path.exists():
                raise FileNotFoundError(
                    f"Source file {source_path} does not exist."
                )
            shutil.copy2(source_path, path)
        elif base64_content is not None:
            try:
                # Strip potential headers or whitespace
                clean_base64 = base64_content.strip()
                if "," in clean_base64:  # Handle data URLs like data:image/png;base64,...
                    clean_base64 = clean_base64.split(",", 1)[1]
                file_bytes = base64.b64decode(clean_base64)
            except Exception as e:
                raise ValueError(f"Invalid base64 content: {str(e)}")
            
            with open(path, "wb") as f:
                f.write(file_bytes)
        else:
            raise ValueError(
                "Either 'source_path' or 'base64_content' must be provided."
            )

        from sankalit_mcp.storage.file_writer import FileWriter
        return FileWriter.get_file_metadata(path)
