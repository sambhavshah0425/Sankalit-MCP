from mcp.server.fastmcp import FastMCP
from sankalit_mcp.tools.create_document import create_document
from sankalit_mcp.tools.read_document import read_document
from sankalit_mcp.tools.list_directory import list_directory
from sankalit_mcp.tools.list_tree import list_tree
from sankalit_mcp.tools.find_documents import find_documents
from sankalit_mcp.tools.document_info import document_info
from sankalit_mcp.tools.copy_document import copy_document
from sankalit_mcp.tools.move_document import move_document
from sankalit_mcp.tools.rename_document import rename_document
from sankalit_mcp.tools.delete_document import delete_document
from sankalit_mcp.tools.create_directory import create_directory
from sankalit_mcp.tools.write_binary_file import write_binary_file
from sankalit_mcp.tools.get_brand_guidelines import get_brand_guidelines
from sankalit_mcp.config import ROOT_DIRECTORY, WORKSPACE_ROOTS

mcp = FastMCP("Sankalit MCP")

# Run compilation check on startup
from sankalit_mcp.services.brand.brand_compiler import BrandCompiler
try:
    BrandCompiler().compile_if_needed()
except Exception as e:
    import sys
    print(f"Error checking brand compilation: {str(e)}", file=sys.stderr)


@mcp.tool()
def hello(name: str) -> str:
    """Test tool."""
    return f"Hello {name}! Sankalit MCP is working."


@mcp.tool(name="create_document")
@mcp.tool()
def create_document_tool(
    path: str = "",
    text_content: str = "",
    structured_content: dict = None,
    document_type: str = None,
    overwrite: bool = False,
    output_path: str = "",
    content: str = "",
):
    """
    Create a document (supports text formats like .txt, .md, and branded documents like .docx, .pdf).
    Provide text_content for raw parsing or structured_content for template-driven creation.
    
    CRITICAL: When the user requests a DOCX or PDF report, call this tool (create_document) directly
    with the target destination path (e.g. path="Z:\\Report.pdf"). Do not generate a temporary
    file and do not call write_binary_file afterward.
    
    Always explicitly pass the correct 'document_type' string:
      - 'technical_report': Use for summary reports, engineering studies, design documents, and general technical reports.
      - 'proposal': Use for project bids, service proposals, and pitch documents.
      - 'meeting_minutes': Use for meeting minutes (MOM) and weekly alignment notes.
      - 'presentation': Use for slide layouts and presentation slides.
    Do not let the system guess the template type from the file name.

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
    return create_document(
        path=path,
        text_content=text_content,
        structured_content=structured_content,
        document_type=document_type,
        overwrite=overwrite,
        output_path=output_path,
        content=content,
    )


@mcp.tool(name="write_binary_file")
@mcp.tool()
def write_binary_file_tool(
    destination: str = "",
    source_path: str = None,
    base64_content: str = None,
    overwrite: bool = False,
    path: str = "",
):
    """
    Copies an existing binary file to the destination, or writes base64 decoded data.
    
    CRITICAL: Prefer using 'source_path' whenever the file already exists on disk (e.g., temporary PDFs, DOCX, or downloads).
    Only use 'base64_content' if the binary exists strictly in memory.
    
    Examples:
      - Copy file from disk:
        write_binary_file(source_path="/tmp/report.pdf", destination="Z:\\Airport Report.pdf")
      - Write base64 from memory:
        write_binary_file(base64_content="...", destination="Z:\\Airport Report.pdf")
    """
    return write_binary_file(
        destination=destination,
        source_path=source_path,
        base64_content=base64_content,
        overwrite=overwrite,
        path=path,
    )


@mcp.tool(name="read_document")
@mcp.tool()
def read_document_tool(
    path: str,
):
    """
    Read a supported document.
    """
    return read_document(path)


@mcp.tool(name="list_directory")
@mcp.tool()
def list_directory_tool(path: str = ""):
    """
    List folders and files in a directory.
    Returns 'folders'/'files' (names) plus 'items' (each with its full path)
    so you can descend into any child directory directly.
    """
    return list_directory(path)


@mcp.tool(name="list_tree")
@mcp.tool()
def list_tree_tool(path: str = "", max_depth: int = 3) -> dict:
    """
    Recursively list a directory as a nested tree up to `max_depth` levels
    deep (default 3, max 15). Use this to explore folder-inside-folder
    structures in a single call, e.g. Z:\\10. Proposal\\<folder>\\<folder>\\...
    Each node includes its full 'path' so you can read files or list deeper.
    """
    return list_tree(path=path, max_depth=max_depth)


@mcp.tool(name="list_allowed_directories")
@mcp.tool()
def list_allowed_directories_tool() -> dict:
    """
    List the directories that this server is allowed to access.
    """
    return {
        "directories": [
            {
                "name": root.name if root.name else str(root),
                "path": str(root),
            }
            for root in WORKSPACE_ROOTS
        ]
    }


@mcp.tool(name="find_documents")
@mcp.tool()
def find_documents_tool(
    path: str = "",
    query: str = "",
    extension: str = "",
):
    """
    Search recursively for matching documents.
    """
    return find_documents(
        path=path,
        query=query,
        extension=extension or None,
    )


@mcp.tool(name="document_info")
@mcp.tool()
def document_info_tool(path: str):
    """
    Get metadata for a document (size, timestamps, format).
    """
    return document_info(path)


@mcp.tool(name="copy_document")
@mcp.tool()
def copy_document_tool(
    source: str,
    destination: str,
):
    """
    Copy a document.
    """
    return copy_document(source, destination)


@mcp.tool(name="move_document")
@mcp.tool()
def move_document_tool(
    source: str,
    destination: str,
):
    """
    Move a document.
    """
    return move_document(source, destination)


@mcp.tool(name="rename_document")
@mcp.tool()
def rename_document_tool(
    source: str,
    new_name: str,
):
    """
    Rename a document.
    """
    return rename_document(source, new_name)


@mcp.tool(name="delete_document")
@mcp.tool()
def delete_document_tool(
    path: str,
):
    """
    Delete a document.
    """
    return delete_document(path)


@mcp.tool(name="create_directory")
@mcp.tool()
def create_directory_tool(
    path: str,
):
    """
    Create a directory.
    """
    return create_directory(path)

@mcp.resource("brand://instructions")
def brand_instructions() -> str:
    """
    Get the compiled markdown branding guidelines and layout rules for Sankalit Consultant documents.
    """
    from sankalit_mcp.services.brand.brand_cache import BrandCache
    return BrandCache.load_instructions()

@mcp.tool(name="get_brand_guidelines")
@mcp.tool()
def get_brand_guidelines_tool() -> str:
    """
    Get the compiled markdown branding guidelines and layout rules for Sankalit Consultant documents.
    """
    return get_brand_guidelines()


def main():
    mcp.run()


if __name__ == "__main__":
    main()