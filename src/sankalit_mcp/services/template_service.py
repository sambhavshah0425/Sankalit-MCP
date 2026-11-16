from pathlib import Path
from docx import Document
from sankalit_mcp.templates.registry import TemplateRegistry
from sankalit_mcp.styles.style_engine import StyleEngine
from sankalit_mcp.handlers.docx import DOCXHandler
from sankalit_mcp.utils.paths import resolve_path
from sankalit_mcp.utils.validation import validate_parent_exists


class TemplateService:

    def __init__(self):
        self.registry = TemplateRegistry()
        self.engine = StyleEngine()
        self.handler = DOCXHandler()

    def generate_document(
        self,
        template_name: str,
        data,
        output_path: str,
        overwrite: bool = False,
    ) -> dict:
        file_path = resolve_path(output_path)
        validate_parent_exists(file_path)

        # Resolve template
        template = self.registry.get(template_name)

        # Create document and populate
        doc = Document()
        
        # Set core property title
        if hasattr(data, "title") and data.title:
            doc.core_properties.title = data.title
            
        template.generate(doc, data, self.engine)
        if file_path.suffix == ".docx":
            # Save via DOCXHandler
            return self.handler.write_document(file_path, doc, overwrite)
        elif file_path.suffix == ".pdf":
            import tempfile
            from sankalit_mcp.storage.file_writer import FileWriter

            if file_path.exists() and not overwrite:
                raise FileExistsError(
                    f"{file_path} already exists."
                )

            # Generate DOCX in a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_docx_path = Path(temp_dir) / "temp.docx"
                self.handler.write_document(temp_docx_path, doc, overwrite=True)
                
                # Convert temporary DOCX to PDF with a 60s timeout
                _convert_with_timeout(temp_docx_path, file_path, timeout_s=60)

            res = FileWriter.get_file_metadata(file_path)
            res["message"] = "PDF document created successfully."
            return res
        else:
            raise ValueError(f"Unsupported output format: {file_path.suffix}")


def _convert_with_timeout(temp_docx_path: Path, file_path: Path, timeout_s: int = 60) -> None:
    from docx2pdf import convert
    import threading
    import pythoncom
    
    error = {}
    
    def _run():
        pythoncom.CoInitialize()
        try:
            convert(str(temp_docx_path), str(file_path))
        except Exception as e:
            error["exc"] = e
        finally:
            pythoncom.CoUninitialize()
            
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout_s)
    
    if t.is_alive():
        raise TimeoutError(
            f"docx2pdf conversion exceeded {timeout_s}s — Word/LibreOffice "
            "likely hung or is showing a dialog. Close any open Word/LibreOffice "
            "instances and retry."
        )
        
    if "exc" in error:
        raise error["exc"]
