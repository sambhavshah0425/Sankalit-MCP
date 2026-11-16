from sankalit_mcp.services.directory_service import DirectoryService

service = DirectoryService()


def list_tree(path: str = "", max_depth: int = 3) -> dict:
    return service.list_tree(path, max_depth)
