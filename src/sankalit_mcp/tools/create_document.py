from typing import Optional
from sankalit_mcp.services.document_service import DocumentService

service = DocumentService()


def create_document(
    path: str = "",
    text_content: str = "",
    structured_content: Optional[dict] = None,
    document_type: Optional[str] = None,
    overwrite: bool = False,
    output_path: str = "",
    content: str = "",
):
    """
    Create a document.

    structured_content schema (technical_report / proposal):
    {
      "title": str,
      "client": str,          # optional - omit to leave off the cover block
      "project_name": str,    # optional
      "location": str,        # optional
      "discipline": str,      # optional
      "prepared_by": str,     # optional
      "reviewed_by": str,     # optional
      "approved_by": str,     # optional
      "revision": str,        # optional (defaults to 'Rev 00')
      "date": str,            # optional (defaults to today's date)
      "doc_no": str,          # optional
      "classification": str,  # optional (defaults to 'Private & Confidential')
      "show_toc": bool,       # optional (defaults to False)
      "sections": [
        {"heading": str, "text": str, "level": 1}
      ],
      "assumptions": [str],   # optional
      "revisions": [          # optional
        {"rev": str, "date": str, "prepared_by": str, "description": str}
      ]
    }
    """
    target_path = output_path or path
    if not target_path:
        raise ValueError("Either 'path' or 'output_path' must be provided.")

    return service.create(
        path=target_path,
        content=content,
        text_content=text_content,
        structured_content=structured_content,
        document_type=document_type,
        overwrite=overwrite,
    )
