import shutil
from sankalit_mcp.registry import HandlerRegistry
from sankalit_mcp.utils.paths import resolve_path
from sankalit_mcp.utils.validation import (
    validate_extension,
    validate_parent_exists,
)


class DocumentService:
    def __init__(self):
        self.registry = HandlerRegistry()

    def create(
        self,
        path: str,
        content: str = "",
        text_content: str = "",
        structured_content: dict = None,
        document_type: str = None,
        overwrite: bool = False,
    ):
        # Resolve content inputs
        actual_text = text_content or (content if isinstance(content, str) else "")
        actual_struct = structured_content or (content if isinstance(content, dict) else None)

        file_path = resolve_path(path)

        validate_extension(file_path)
        validate_parent_exists(file_path)

        if file_path.suffix in [".docx", ".pdf"]:
            from sankalit_mcp.services.template_service import TemplateService
            from sankalit_mcp.templates.models import get_model_for_template, TechnicalReportData
            from sankalit_mcp.templates.prompt_analyzer import PromptAnalyzer
            
            # Determine the template name
            VALID_DOCUMENT_TYPES = {
                "technical_report",
                "proposal",
                "meeting_minutes",
                "presentation",
            }
            if document_type:
                normalized_type = document_type.lower().strip()
                if normalized_type not in VALID_DOCUMENT_TYPES:
                    raise ValueError(
                        f"Invalid document_type '{document_type}'. "
                        f"Must be one of: {', '.join(sorted(VALID_DOCUMENT_TYPES))}"
                    )
                template_name = normalized_type
            else:
                intent = PromptAnalyzer.analyze(path + " " + actual_text)
                template_name = intent.template if intent else None
                if not template_name:
                    template_name = "technical_report"
            import sys
            print(f"Using template: {template_name}", file=sys.stderr)

            if actual_struct is not None:
                # Use structured content directly
                model_cls = get_model_for_template(template_name)
                data = model_cls.from_dict(actual_struct)
            else:
                # Direct parsing from_text, bypassing the unused BrandContext indirection
                data = TechnicalReportData.from_text(actual_text)
            
            # Guard: Ensure content is generated and non-trivial on the parsed model
            self._assert_non_trivial_content(data)
            
            template_service = TemplateService()
            return template_service.generate_document(
                template_name,
                data,
                str(file_path),
                overwrite,
            )

        # For non-docx formats
        if actual_struct is not None:
            # Format dictionary structure nicely as markdown/text
            title = actual_struct.get("title", "Document")
            lines = [f"# {title}"]
            if "project_name" in actual_struct:
                lines.append(f"Project: {actual_struct['project_name']}")
            if "client" in actual_struct:
                lines.append(f"Client: {actual_struct['client']}")
            lines.append("")
            
            for section in actual_struct.get("sections", []):
                h_level = "#" * section.get("level", 1)
                lines.append(f"{h_level} {section.get('heading', '')}")
                lines.append(section.get("text", ""))
                lines.append("")
            write_content = "\n".join(lines)
        else:
            write_content = actual_text

        handler = self.registry.get_handler(file_path.suffix)

        return handler.write(
            file_path,
            write_content,
            overwrite,
        )

    def read(
        self,
        path: str,
    ):
        file_path = resolve_path(path)

        validate_extension(file_path)

        handler = self.registry.get_handler(file_path.suffix)

        return handler.read(file_path)

    def copy(
        self,
        source: str,
        destination: str,
    ) -> dict:
        src_path = resolve_path(source)
        dest_path = resolve_path(destination)

        if not src_path.exists():
            raise FileNotFoundError(
                f"Source file {src_path} does not exist."
            )

        if not dest_path.parent.exists():
            raise FileNotFoundError(
                f"Destination parent directory {dest_path.parent} does not exist."
            )

        shutil.copy2(src_path, dest_path)

        return {
            "success": True,
            "source": str(src_path),
            "destination": str(dest_path),
            "message": f"Copied {src_path} to {dest_path} successfully.",
        }

    def move(
        self,
        source: str,
        destination: str,
    ) -> dict:
        src_path = resolve_path(source)
        dest_path = resolve_path(destination)

        if not src_path.exists():
            raise FileNotFoundError(
                f"Source file {src_path} does not exist."
            )

        if not dest_path.parent.exists():
            raise FileNotFoundError(
                f"Destination parent directory {dest_path.parent} does not exist."
            )

        shutil.move(str(src_path), str(dest_path))

        return {
            "success": True,
            "source": str(src_path),
            "destination": str(dest_path),
            "message": f"Moved {src_path} to {dest_path} successfully.",
        }

    def rename(
        self,
        source: str,
        new_name: str,
    ) -> dict:
        src_path = resolve_path(source)

        if not src_path.exists():
            raise FileNotFoundError(
                f"Source file {src_path} does not exist."
            )

        dest_path = src_path.parent / new_name

        src_path.rename(dest_path)

        return {
            "success": True,
            "source": str(src_path),
            "destination": str(dest_path),
            "message": f"Renamed {src_path.name} to {dest_path.name} successfully.",
        }

    def delete(
        self,
        path: str,
    ) -> dict:
        file_path = resolve_path(path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"File {file_path} does not exist."
            )

        if not file_path.is_file():
            raise ValueError(
                f"Path {file_path} is not a file."
            )

        file_path.unlink()

        return {
            "success": True,
            "path": str(file_path),
            "message": "File deleted successfully.",
        }

    def _assert_non_trivial_content(self, data) -> None:
        """
        Validates that the parsed document data contains real content,
        checking the appropriate fields depending on the data model type.
        """
        is_empty = True
        
        # Case 1: Has sections (TechnicalReportData, ProposalData)
        if hasattr(data, "sections") and data.sections:
            # Require that sections actually carry body text, not just headings.
            # A document made of headings with no body content is not usable output.
            sections_with_body = [s for s in data.sections if s.text.strip()]
            if not sections_with_body:
                raise ValueError(
                    "The report has section headings but no body text under any of "
                    "them. This usually means the source document's content couldn't "
                    "be extracted (e.g. it's image/diagram-based rather than text), "
                    "or the summarization step only produced an outline. Provide "
                    "actual paragraph content under each heading before creating the document."
                )
            empty_headings = [s.heading for s in data.sections if not s.text.strip()]
            if empty_headings:
                import sys
                print(
                    f"WARNING: {len(empty_headings)} section(s) have no body text: "
                    f"{empty_headings}",
                    file=sys.stderr,
                )
            is_empty = False
                
        # Case 2: Has slides (PresentationData)
        elif hasattr(data, "slides") and data.slides:
            is_empty = False
            
        # Case 3: Has meeting minutes details (MeetingMinutesData)
        elif hasattr(data, "attendees") or hasattr(data, "discussion_points"):
            attendees = getattr(data, "attendees", [])
            discussion_points = getattr(data, "discussion_points", [])
            if attendees or discussion_points:
                is_empty = False
                
        if is_empty:
            raise ValueError(
                "The report content is empty. Please provide the complete content "
                "before creating the document."
            )
