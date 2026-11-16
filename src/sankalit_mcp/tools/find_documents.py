from sankalit_mcp.services.search_service import SearchService

service = SearchService()


def find_documents(
    path: str = "",
    query: str = "",
    extension: str | None = None,
):
    return service.find_documents(
        path=path,
        query=query,
        extension=extension,
    )
