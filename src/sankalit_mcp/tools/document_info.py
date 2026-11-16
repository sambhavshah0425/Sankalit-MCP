from sankalit_mcp.services.metadata_service import MetadataService

service = MetadataService()


def document_info(path: str) -> dict:
    """
    Get metadata for a document.
    """
    return service.get_info(path)
