from sankalit_mcp.services.document_service import DocumentService

service = DocumentService()


def delete_document(
    path: str,
) -> dict:
    """
    Delete a document.
    """
    return service.delete(path)
