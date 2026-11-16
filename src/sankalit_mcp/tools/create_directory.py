from sankalit_mcp.services.directory_service import DirectoryService

service = DirectoryService()


def create_directory(
    path: str,
) -> dict:
    """
    Create a directory.
    """
    return service.create_directory(path)
