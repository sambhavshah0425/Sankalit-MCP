from pathlib import Path

from sankalit_mcp.utils.paths import resolve_path


class DirectoryService:

    def list_directory(self, path: str = "") -> dict:
        """
        List folders and files in a directory.
        """

        directory = resolve_path(path)

        if not directory.exists():
            raise FileNotFoundError(
                f"{directory} does not exist."
            )

        if not directory.is_dir():
            raise NotADirectoryError(
                f"{directory} is not a directory."
            )

        folders = []
        files = []
        items = []

        for item in sorted(directory.iterdir()):
            if item.is_dir():
                folders.append(item.name)
                items.append({"name": item.name, "path": str(item), "type": "folder"})
            else:
                files.append(item.name)
                items.append({"name": item.name, "path": str(item), "type": "file"})

        return {
            "path": str(directory),
            "folders": folders,
            "files": files,
            # Full paths for each entry so callers can navigate deeper without
            # having to reconstruct child paths themselves.
            "items": items,
        }

    def list_tree(self, path: str = "", max_depth: int = 3) -> dict:
        """
        Recursively list a directory as a nested tree, up to max_depth levels
        deep. Each node carries its full path so callers can descend reliably
        into folder-inside-folder structures in a single call.
        """

        # Clamp depth to a sane range to avoid runaway walks over huge shares.
        try:
            max_depth = int(max_depth)
        except (TypeError, ValueError):
            max_depth = 3
        max_depth = max(1, min(max_depth, 15))

        root = resolve_path(path)

        if not root.exists():
            raise FileNotFoundError(f"{root} does not exist.")

        if not root.is_dir():
            raise NotADirectoryError(f"{root} is not a directory.")

        def walk(directory: Path, depth: int) -> dict:
            node = {
                "name": directory.name or str(directory),
                "path": str(directory),
                "type": "folder",
                "children": [],
            }

            if depth >= max_depth:
                node["truncated"] = True
                return node

            try:
                entries = sorted(directory.iterdir())
            except PermissionError:
                node["error"] = "permission denied"
                return node
            except OSError as exc:
                node["error"] = str(exc)
                return node

            for item in entries:
                if item.is_dir():
                    node["children"].append(walk(item, depth + 1))
                else:
                    node["children"].append(
                        {"name": item.name, "path": str(item), "type": "file"}
                    )

            return node

        return walk(root, 0)

    def create_directory(self, path: str) -> dict:
        dir_path = resolve_path(path)

        if dir_path.exists():
            raise FileExistsError(
                f"Path {dir_path} already exists."
            )

        dir_path.mkdir(parents=True, exist_ok=False)

        return {
            "success": True,
            "path": str(dir_path),
            "message": f"Directory {dir_path.name} created successfully.",
        }
