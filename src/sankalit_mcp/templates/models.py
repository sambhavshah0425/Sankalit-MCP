from dataclasses import dataclass, field
from typing import List


@dataclass
class RevisionInfo:
    rev: str
    date: str
    prepared_by: str
    description: str


@dataclass
class Abbreviation:
    term: str
    definition: str


@dataclass
class SectionContent:
    heading: str
    text: str
    level: int = 1


@dataclass
class BaseDocumentData:
    title: str
    project_name: str = ""
    client: str = ""
    location: str = ""
    discipline: str = ""
    prepared_by: str = ""
    reviewed_by: str = ""
    approved_by: str = ""
    revision: str = "Rev 00"
    date: str = ""
    doc_no: str = ""
    classification: str = "Private & Confidential"

    @classmethod
    def get_base_kwargs(cls, data_dict: dict) -> dict:
        from datetime import date as _date
        return {
            "title": data_dict.get("title", "Sankalit Document"),
            "project_name": data_dict.get("project_name", ""),
            "client": data_dict.get("client", ""),
            "location": data_dict.get("location", ""),
            "discipline": data_dict.get("discipline", ""),
            "prepared_by": data_dict.get("prepared_by", ""),
            "reviewed_by": data_dict.get("reviewed_by", ""),
            "approved_by": data_dict.get("approved_by", ""),
            "revision": data_dict.get("revision", "Rev 00"),
            "date": data_dict.get("date", _date.today().strftime("%d %B %Y")),
            "doc_no": data_dict.get("doc_no", ""),
            "classification": data_dict.get("classification", "Private & Confidential"),
        }


@dataclass
class TechnicalReportData(BaseDocumentData):
    assumptions: List[str] = field(default_factory=list)
    revisions: List[RevisionInfo] = field(default_factory=list)
    abbreviations: List[Abbreviation] = field(default_factory=list)
    sections: List[SectionContent] = field(default_factory=list)
    annexures: List[str] = field(default_factory=list)
    parse_warnings: List[str] = field(default_factory=list)
    show_toc: bool = False

    @classmethod
    def from_dict(cls, data_dict: dict) -> "TechnicalReportData":
        kwargs = cls.get_base_kwargs(data_dict)
        
        # Extract revisions
        raw_revisions = data_dict.get("revisions", [])
        revisions = []
        for r in raw_revisions:
            if isinstance(r, dict):
                revisions.append(RevisionInfo(
                    rev=r.get("rev", ""),
                    date=r.get("date", ""),
                    prepared_by=r.get("prepared_by", ""),
                    description=r.get("description", "")
                ))
            elif isinstance(r, RevisionInfo):
                revisions.append(r)

        # Extract abbreviations
        raw_abbreviations = data_dict.get("abbreviations", [])
        abbreviations = []
        for a in raw_abbreviations:
            if isinstance(a, dict):
                abbreviations.append(Abbreviation(
                    term=a.get("term", ""),
                    definition=a.get("definition", "")
                ))
            elif isinstance(a, Abbreviation):
                abbreviations.append(a)

        # Extract sections
        raw_sections = data_dict.get("sections", [])
        sections = []
        for s in raw_sections:
            if isinstance(s, dict):
                sections.append(SectionContent(
                    heading=s.get("heading", ""),
                    text=s.get("text", ""),
                    level=s.get("level", 1)
                ))
            elif isinstance(s, SectionContent):
                sections.append(s)

        return cls(
            assumptions=data_dict.get("assumptions", []),
            revisions=revisions,
            abbreviations=abbreviations,
            sections=sections,
            annexures=data_dict.get("annexures", []),
            parse_warnings=data_dict.get("parse_warnings", []),
            show_toc=data_dict.get("show_toc", False),
            **kwargs
        )

    @classmethod
    def from_text(cls, content: str) -> "TechnicalReportData":
        """
        Parses raw text/markdown into structured TechnicalReportData.
        """
        lines = content.split('\n')
        
        # Default fallback values
        title = "Sankalit Technical Report"
        project_name = ""
        client = ""
        location = ""
        discipline = ""
        prepared_by = ""
        reviewed_by = ""
        approved_by = ""
        revision = "Rev 00"
        from datetime import date as _date
        date = _date.today().strftime("%d %B %Y")
        doc_no = ""
        classification = "Private & Confidential"
        show_toc = False
        
        assumptions = []
        revisions = []
        abbreviations = []
        sections = []
        annexures = []
        parse_warnings = []
        
        current_section_title = None
        current_section_text = []
        current_section_level = 1
        
        in_assumptions = False
        in_revisions = False
        in_abbreviations = False
        in_annexures = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
                
            # Parse key-value metadata lines if present
            lower_stripped = stripped.lower()
            if lower_stripped.startswith("project name:"):
                project_name = stripped[len("project name:"):].strip()
                continue
            elif lower_stripped.startswith("project:"):
                project_name = stripped[len("project:"):].strip()
                continue
            elif lower_stripped.startswith("client:"):
                client = stripped[len("client:"):].strip()
                continue
            elif lower_stripped.startswith("location:"):
                location = stripped[len("location:"):].strip()
                continue
            elif lower_stripped.startswith("discipline:"):
                discipline = stripped[len("discipline:"):].strip()
                continue
            elif lower_stripped.startswith("prepared by:"):
                prepared_by = stripped[len("prepared by:"):].strip()
                continue
            elif lower_stripped.startswith("doc no:"):
                doc_no = stripped[len("doc no:"):].strip()
                continue
            elif lower_stripped.startswith("revision:"):
                revision = stripped[len("revision:"):].strip()
                continue
            elif lower_stripped.startswith("date:"):
                date = stripped[len("date:"):].strip()
                continue
            elif lower_stripped.startswith("classification:"):
                classification = stripped[len("classification:"):].strip()
                continue
            elif lower_stripped.startswith("show_toc:"):
                show_toc = stripped[len("show_toc:"):].strip().lower() in ("true", "yes", "1")
                continue
                
            # Detect Markdown Headings
            heading_level = 0
            h_text = ""
            if stripped.startswith("# "):
                heading_level = 1
                h_text = stripped[2:].strip()
            elif stripped.startswith("## "):
                heading_level = 2
                h_text = stripped[3:].strip()
            elif stripped.startswith("### "):
                heading_level = 3
                h_text = stripped[4:].strip()

            if heading_level > 0:
                # Save previous section first
                if current_section_title:
                    sections.append(SectionContent(
                        current_section_title, 
                        "\n".join(current_section_text), 
                        current_section_level
                    ))
                
                if heading_level == 1 and title == "Sankalit Technical Report":
                    title = h_text  # Use the first major heading as Title
                    current_section_title = None
                    current_section_text = []
                    continue
                
                current_section_title = h_text
                current_section_text = []
                current_section_level = heading_level
                
                h_text_lower = h_text.lower()
                in_assumptions = "assumptions" in h_text_lower
                in_revisions = "revision" in h_text_lower
                in_abbreviations = "abbreviation" in h_text_lower
                in_annexures = "annexure" in h_text_lower
                
                if in_annexures:
                    current_section_title = None
                continue
                
            # Parse list/table contents
            if in_assumptions:
                if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("• "):
                    assumptions.append(stripped[2:])
                else:
                    assumptions.append(stripped)
            elif in_revisions:
                parts = [p.strip() for p in stripped.split("|")]
                if len(parts) >= 4:
                    revisions.append(RevisionInfo(parts[0], parts[1], parts[2], parts[3]))
            elif in_abbreviations:
                if " - " in stripped:
                    term, val = stripped.split(" - ", 1)
                    abbreviations.append(Abbreviation(term.strip(), val.strip()))
                elif ":" in stripped:
                    term, val = stripped.split(":", 1)
                    abbreviations.append(Abbreviation(term.strip(), val.strip()))
            elif in_annexures:
                annexures.append(stripped)
            else:
                if current_section_title:
                    current_section_text.append(line)
                else:
                    current_section_title = "Introduction"
                    current_section_text = [line]
                    current_section_level = 1
                    parse_warnings.append("Orphan text captured in implicit 'Introduction' section.")
                    
        # Append final section
        if current_section_title:
            sections.append(SectionContent(
                current_section_title, 
                "\n".join(current_section_text), 
                current_section_level
            ))

        # Drop stray bare-URL/branding lines (e.g. a trailing "sankalit.in")
        # that sometimes end up appended to the last section's body. The
        # masthead and footer already carry this branding, so it's just
        # noise/duplication when it shows up mid-body.
        import re
        url_only_pattern = re.compile(
            r"^(https?://)?(www\.)?[a-z0-9-]+\.[a-z]{2,}/?$", re.IGNORECASE
        )
        for s in sections:
            lines = [ln for ln in s.text.split("\n") if not url_only_pattern.match(ln.strip())]
            s.text = "\n".join(lines).strip()
            
        # Standard defaults if not parsed
        if not revisions:
            revisions = [
                RevisionInfo(
                    "Rev 00",
                    date,
                    prepared_by,
                    "Initial Issue"
                )
            ]

        # Leave assumptions and abbreviations empty unless supplied
        assumptions = assumptions or []
        abbreviations = abbreviations or []
            
        return cls(
            title=title,
            project_name=project_name,
            client=client,
            location=location,
            discipline=discipline,
            prepared_by=prepared_by,
            reviewed_by=reviewed_by,
            approved_by=approved_by,
            revision=revision,
            date=date,
            doc_no=doc_no,
            classification=classification,
            assumptions=assumptions,
            revisions=revisions,
            abbreviations=abbreviations,
            sections=sections,
            annexures=annexures,
            parse_warnings=parse_warnings,
            show_toc=show_toc
        )


@dataclass
class ProposalData(BaseDocumentData):
    sections: List[SectionContent] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data_dict: dict) -> "ProposalData":
        kwargs = cls.get_base_kwargs(data_dict)
        
        raw_sections = data_dict.get("sections", [])
        sections = []
        for s in raw_sections:
            if isinstance(s, dict):
                sections.append(SectionContent(
                    heading=s.get("heading", ""),
                    text=s.get("text", ""),
                    level=s.get("level", 1)
                ))
            elif isinstance(s, SectionContent):
                sections.append(s)

        return cls(
            sections=sections,
            **kwargs
        )


@dataclass
class MeetingMinutesData(BaseDocumentData):
    attendees: List[str] = field(default_factory=list)
    discussion_points: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data_dict: dict) -> "MeetingMinutesData":
        kwargs = cls.get_base_kwargs(data_dict)
        return cls(
            attendees=data_dict.get("attendees", []),
            discussion_points=data_dict.get("discussion_points", []),
            **kwargs
        )


@dataclass
class PresentationData(BaseDocumentData):
    slides: List[dict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data_dict: dict) -> "PresentationData":
        kwargs = cls.get_base_kwargs(data_dict)
        return cls(
            slides=data_dict.get("slides", []),
            **kwargs
        )


TEMPLATE_MODEL_MAP = {
    "technical_report": TechnicalReportData,
    "proposal": ProposalData,
    "meeting_minutes": MeetingMinutesData,
    "presentation": PresentationData,
}


def get_model_for_template(template_name: str):
    name = template_name.lower()
    model_cls = TEMPLATE_MODEL_MAP.get(name)
    if not model_cls:
        raise ValueError(f"No data model registered for template '{template_name}'")
    return model_cls

