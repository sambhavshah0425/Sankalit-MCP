from sankalit_mcp.templates.technical_report import TechnicalReportTemplate
from sankalit_mcp.templates.proposal import ProposalTemplate
from sankalit_mcp.templates.presentation import PresentationTemplate
from sankalit_mcp.templates.meeting_minutes import MeetingMinutesTemplate


class TemplateRegistry:
    _templates = {
        "technical_report": TechnicalReportTemplate(),
        "proposal": ProposalTemplate(),
        "presentation": PresentationTemplate(),
        "meeting_minutes": MeetingMinutesTemplate(),
    }

    @classmethod
    def get(cls, template_name: str):
        template = cls._templates.get(template_name.lower())
        if not template:
            raise ValueError(f"No template registered for '{template_name}'")
        return template
