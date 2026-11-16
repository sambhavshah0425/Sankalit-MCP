from sankalit_mcp.services.document_service import DocumentService

service = DocumentService()


def move_document(
    source: str,
    destination: str,
) -> dict:
    """
    Move a document.
    """
    return service.move(source, destination)
