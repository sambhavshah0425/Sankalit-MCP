from sankalit_mcp.services.document_service import DocumentService

service = DocumentService()


def read_document(
    path: str,
) -> str:
    return service.read(path)
