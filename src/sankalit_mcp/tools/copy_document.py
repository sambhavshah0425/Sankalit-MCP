from sankalit_mcp.services.document_service import DocumentService

service = DocumentService()


def copy_document(
    source: str,
    destination: str,
) -> dict:
    """
    Copy a document.
    """
    return service.copy(source, destination)
