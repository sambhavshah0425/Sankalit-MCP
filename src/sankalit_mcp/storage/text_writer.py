from pathlib import Path


class TextWriter:

    @staticmethod
    def write(
        path: Path,
        content: str,
        overwrite: bool = False,
    ) -> dict:
        if path.exists() and not overwrite:
            raise FileExistsError(f"Destination file {path} already exists.")

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        from sankalit_mcp.storage.file_writer import FileWriter
        return FileWriter.get_file_metadata(path)
