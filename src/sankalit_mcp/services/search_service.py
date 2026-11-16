from pathlib import Path

from sankalit_mcp.utils.paths import resolve_path


class SearchService:

    def find_documents(
        self,
        path: str = "",
        query: str = "",
        extension: str | None = None,
    ) -> dict:
        """
        Recursively search for documents.
        """

        root = resolve_path(path)

        if not root.exists():
            raise FileNotFoundError(
                f"{root} does not exist."
            )

        results = []

        for item in root.rglob("*"):

            if not item.is_file():
                continue

            if query and query.lower() not in item.name.lower():
                continue

            if extension and item.suffix.lower() != extension.lower():
                continue

            results.append(
                {
                    "name": item.name,
                    "path": str(item),
                    "extension": item.suffix,
                }
            )

        return {
            "count": len(results),
            "results": results,
        }
