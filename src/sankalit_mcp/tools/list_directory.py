from sankalit_mcp.services.directory_service import DirectoryService

service = DirectoryService()


def list_directory(path: str = "") -> dict:
    return service.list_directory(path)
