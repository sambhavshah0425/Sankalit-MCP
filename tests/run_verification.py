import sys
import time
from pathlib import Path
from docx import Document

# Adjust python path to find sankalit_mcp
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sankalit_mcp.services.document_service import DocumentService
from sankalit_mcp.styles.style_engine import StyleEngine
from sankalit_mcp.brand.registry import RuleRegistry
from sankalit_mcp.brand.validator import BrandValidator
from sankalit_mcp.brand.context import ValidationContext
from sankalit_mcp.brand.compliance_report import ComplianceReportFormatter

# Import all rules
from sankalit_mcp.brand.rules.typography.font001 import Font001Rule
from sankalit_mcp.brand.rules.typography.font002 import Font002Rule
from sankalit_mcp.brand.rules.watermark.wm001 import Wm001Rule
from sankalit_mcp.brand.rules.toc.toc001 import Toc001Rule
from sankalit_mcp.brand.rules.metadata.meta001 import Meta001Rule
from sankalit_mcp.brand.rules.header.header001 import Header001Rule
from sankalit_mcp.brand.rules.footer.footer001 import Footer001Rule
from sankalit_mcp.brand.rules.document.doc002 import Doc002Rule
from sankalit_mcp.brand.rules.document.doc001 import Doc001Rule
from sankalit_mcp.brand.rules.cover.cover001 import Cover001Rule

def safe_unlink(path):
    p = Path(path)
    for _ in range(10):
        try:
            if p.exists():
                p.unlink()
            return
        except PermissionError:
            time.sleep(0.2)
        except Exception:
            pass

def run_e2e_verification():
    doc_service = DocumentService()
    
    # Initialize brand rules registry
    registry = RuleRegistry()
    registry.register(Font001Rule())
    registry.register(Font002Rule())
    registry.register(Wm001Rule())
    registry.register(Toc001Rule())
    registry.register(Meta001Rule())
    registry.register(Header001Rule())
    registry.register(Footer001Rule())
    registry.register(Doc002Rule())
    registry.register(Doc001Rule())
    registry.register(Cover001Rule())
    
    validator = BrandValidator(registry)
    style_engine = StyleEngine()
    style_config = style_engine.get_style()

    print("=" * 60)
    print("STARTING END-TO-END TEMPLATE VERIFICATION")
    print("=" * 60)

    # ----------------------------------------------------
    # 1. Technical Report
    # ----------------------------------------------------
    print("\n--- Verifying Technical Report ---")
    tech_path = "TechnicalReport.docx"
    tech_content = (
        "# Airport Systems Integration Study\n"
        "Project: Terminal expansion\n"
        "## 1. Introduction\n"
        "This is the introduction text for airport terminal expansion.\n"
        "## 2. Methodology\n"
        "Some methodology description here."
    )
    res = doc_service.create(tech_path, tech_content, overwrite=True)
    assert res["success"] is True
    file_path = Path(res["path"])
    print(f"Generated: {file_path}")

    # Inspect
    doc = Document(file_path)
    print(f"Paragraph count: {len(doc.paragraphs)}")
    assert len(doc.paragraphs) > 0, "Technical Report paragraph count should be > 0"
    
    visible_text = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
    assert len(visible_text) > 0, "Technical Report content should be visible"
    
    # Run Validator
    context = ValidationContext(document=doc, style_config=style_config, template_name="technical_report")
    report = validator.validate(context)
    print(ComplianceReportFormatter.format_text(report))
    assert report.error_count == 0, f"Technical Report brand compliance failed with {report.error_count} errors"

    # Cleanup temp file
    safe_unlink(file_path)

    # ----------------------------------------------------
    # 2. Proposal
    # ----------------------------------------------------
    print("\n--- Verifying Proposal ---")
    prop_path = "Proposal.docx"
    prop_content = (
        "# Metro Line Proposal\n"
        "Project: Metro Line 3\n"
        "## 1. Executive Summary\n"
        "This is the summary of Metro Line 3 Proposal.\n"
        "## 2. Project Scope\n"
        "BIM modeling and design scope description."
    )
    res = doc_service.create(prop_path, prop_content, overwrite=True)
    assert res["success"] is True
    file_path = Path(res["path"])
    print(f"Generated: {file_path}")

    doc = Document(file_path)
    print(f"Paragraph count: {len(doc.paragraphs)}")
    assert len(doc.paragraphs) > 0, "Proposal paragraph count should be > 0"
    
    all_text = "\n".join(p.text for p in doc.paragraphs)
    assert "Executive Summary" in all_text, "Executive Summary section should be present"
    assert "Project Scope" in all_text, "Project Scope section should be present"
    print("Proposal layout verified successfully.")

    # Cleanup temp file
    safe_unlink(file_path)

    # ----------------------------------------------------
    # 3. Meeting Minutes
    # ----------------------------------------------------
    print("\n--- Verifying Meeting Minutes ---")
    mm_path = "MeetingMinutes.docx"
    mm_content = (
        "# Weekly Alignment Meeting\n"
        "Project: Runway design\n"
        "## 1. Attendees\n"
        "Attendees list for Runway design project.\n"
        "## 2. Discussion Points\n"
        "BIM modeling and runway scheduling discussion."
    )
    res = doc_service.create(mm_path, mm_content, overwrite=True)
    assert res["success"] is True
    file_path = Path(res["path"])
    print(f"Generated: {file_path}")

    doc = Document(file_path)
    print(f"Paragraph count: {len(doc.paragraphs)}")
    assert len(doc.paragraphs) > 0, "Meeting Minutes paragraph count should be > 0"
    
    all_text = "\n".join(p.text for p in doc.paragraphs)
    assert "Attendees" in all_text, "Attendees section should be present"
    assert "Discussion Points" in all_text, "Discussion Points section should be present"
    print("Meeting Minutes layout verified successfully.")

    # Cleanup temp file
    safe_unlink(file_path)

    # ----------------------------------------------------
    # 4. Presentation
    # ----------------------------------------------------
    print("\n--- Verifying Presentation ---")
    pres_path = "Presentation.docx"
    pres_content = (
        "# Final Pitch Slides\n"
        "Project: Airport tender\n"
        "## Slide 1: Agenda\n"
        "- Slide bullet point 1\n"
        "- Slide bullet point 2"
    )
    res = doc_service.create(pres_path, pres_content, overwrite=True)
    assert res["success"] is True
    file_path = Path(res["path"])
    print(f"Generated: {file_path}")

    doc = Document(file_path)
    print(f"Paragraph count: {len(doc.paragraphs)}")
    assert len(doc.paragraphs) > 0, "Presentation paragraph count should be > 0"
    
    all_text = "\n".join(p.text for p in doc.paragraphs)
    assert "Presentation: Final Pitch Slides" in all_text, "Title slide should be present"
    assert "Slide 1: Agenda" in all_text, "Agenda slide should be present"
    assert "Introduction" in all_text, "Bullet points/Agenda items should be present"
    print("Presentation layout verified successfully.")

    # Cleanup temp file
    safe_unlink(file_path)

    print("\n" + "=" * 60)
    print("ALL E2E VERIFICATIONS PASSED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    run_e2e_verification()
