from sankalit_mcp.services.document_service import DocumentService

service = DocumentService()


def rename_document(
    source: str,
    new_name: str,
) -> dict:
    """
    Rename a document.
    """
    return service.rename(source, new_name)
