import datetime
from pathlib import Path
from sankalit_mcp.utils.paths import resolve_path


class MetadataService:

    def get_info(self, path: str) -> dict:
        file_path = resolve_path(path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"{file_path} does not exist."
            )

        stat = file_path.stat()

        created = datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()
        modified = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()

        return {
            "name": file_path.name,
            "path": str(file_path),
            "extension": file_path.suffix,
            "size": stat.st_size,
            "created": created,
            "modified": modified,
            "is_file": file_path.is_file(),
        }
