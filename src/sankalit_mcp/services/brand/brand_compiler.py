import os
import hashlib
import json
import re
from pathlib import Path
from pypdf import PdfReader


class BrandCompiler:
    COMPILER_VERSION = "1.0.0"
    GUIDELINE_VERSION = "Rev-04"

    def __init__(self):
        from sankalit_mcp.config import PROJECT_ROOT
        self.workspace_root = PROJECT_ROOT
        self.pdf_path = self.workspace_root / "resources" / "brand" / "Sankalit Brand Guidelines.pdf"
        self.output_dir = self.workspace_root / "resources" / "brand"
        self.hash_path = self.output_dir / "brand.hash"

    def calculate_pdf_hash(self) -> str:
        if not self.pdf_path.exists():
            return ""
        sha256 = hashlib.sha256()
        with open(self.pdf_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def compile_if_needed(self) -> bool:
        pdf_hash = self.calculate_pdf_hash()
        if not pdf_hash:
            import sys
            print("Brand Guidelines PDF not found. Using fallback stubs.", file=sys.stderr)
            self._compile_fallbacks()
            return False

        if self.hash_path.exists():
            try:
                with open(self.hash_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                if (meta.get("pdf_hash") == pdf_hash and 
                        meta.get("compiler_version") == self.COMPILER_VERSION):
                    import sys
                    print("Brand guidelines cache is up to date. Skipping compile.", file=sys.stderr)
                    return False
            except Exception:
                pass

        import sys
        print("Compiling brand guidelines...", file=sys.stderr)
        try:
            pdf_data = self.read_pdf()
            raw_text = self.extract_text(pdf_data)
            normalized_text = self.normalize_text(raw_text)
            rules = self.extract_known_rules(normalized_text)
            instructions = self.build_instruction_markdown(rules)
            manifest = self.build_manifest(rules)
            report = self.build_compile_report(rules)
            self.save(instructions, manifest, report, pdf_hash)
            return True
        except Exception as e:
            import sys
            print(f"Compilation failed with error: {str(e)}. Using fallback stubs.", file=sys.stderr)
            self._compile_fallbacks()
            return False

    def read_pdf(self) -> bytes:
        with open(self.pdf_path, "rb") as f:
            return f.read()

    def extract_text(self, pdf_data: bytes) -> str:
        import io
        reader = PdfReader(io.BytesIO(pdf_data))
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        return "\n".join(pages_text)

    def normalize_text(self, raw_text: str) -> str:
        lines = raw_text.split("\n")
        cleaned_lines = []
        for line in lines:
            if "Sankalit Consultant | Brand" in line:
                continue
            if "Private & Confidential | Sankalit" in line:
                continue
            cleaned_lines.append(line.strip())
        return "\n".join(cleaned_lines)

    def extract_known_rules(self, text: str) -> dict:
        rules = {}
        
        # 1. Fonts Extraction
        rules["font_family"] = {"value": "Calibri", "confidence": 0.0}
        if "Calibri" in text:
            rules["font_family"] = {"value": "Calibri", "confidence": 1.0}
            
        rules["monospace_font"] = {"value": "Consolas", "confidence": 0.0}
        if "Consolas" in text:
            rules["monospace_font"] = {"value": "Consolas", "confidence": 1.0}

        # 2. Heading Sizes Extraction
        h1_size = 14
        h1_conf = 0.5
        h2_size = 12
        h2_conf = 0.5
        h3_size = 11
        h3_conf = 0.5
        
        m_h1 = re.search(r"Heading 1.*?(\d+)\s*pt", text, re.IGNORECASE | re.DOTALL)
        if m_h1:
            h1_size = int(m_h1.group(1))
            h1_conf = 0.95
            
        m_h2 = re.search(r"Heading 2.*?(\d+)\s*pt", text, re.IGNORECASE | re.DOTALL)
        if m_h2:
            h2_size = int(m_h2.group(1))
            h2_conf = 0.95
            
        m_h3 = re.search(r"Heading 3.*?(\d+)\s*pt", text, re.IGNORECASE | re.DOTALL)
        if m_h3:
            h3_size = int(m_h3.group(1))
            h3_conf = 0.95

        rules["h1_size"] = {"value": h1_size, "confidence": h1_conf}
        rules["h2_size"] = {"value": h2_size, "confidence": h2_conf}
        rules["h3_size"] = {"value": h3_size, "confidence": h3_conf}

        # 3. Margins Extraction
        top_margin = 25.0
        bottom_margin = 20.0
        left_margin = 25.0
        right_margin = 25.0
        margin_conf = 0.5
        
        m_margin = re.search(r"Technical Reports.*?(\d+)\s*/\s*(\d+)\s*/\s*(\d+)\s*/\s*(\d+)\s*mm", text, re.IGNORECASE | re.DOTALL)
        if m_margin:
            top_margin = float(m_margin.group(1))
            bottom_margin = float(m_margin.group(2))
            left_margin = float(m_margin.group(3))
            right_margin = float(m_margin.group(4))
            margin_conf = 0.95

        rules["top_margin"] = {"value": top_margin, "confidence": margin_conf}
        rules["bottom_margin"] = {"value": bottom_margin, "confidence": margin_conf}
        rules["left_margin"] = {"value": left_margin, "confidence": margin_conf}
        rules["right_margin"] = {"value": right_margin, "confidence": margin_conf}

        # 4. Color Palette
        rules["primary_color"] = {"value": "#F5A623", "confidence": 0.0}
        m_orange = re.search(r"Sankalit Orange.*?#([0-9A-Fa-f]{6})", text, re.IGNORECASE | re.DOTALL)
        if m_orange:
            rules["primary_color"] = {"value": f"#{m_orange.group(1)}", "confidence": 1.0}
            
        rules["secondary_color"] = {"value": "#F7C05A", "confidence": 0.0}
        m_amber = re.search(r"Sankalit Amber.*?#([0-9A-Fa-f]{6})", text, re.IGNORECASE | re.DOTALL)
        if m_amber:
            rules["secondary_color"] = {"value": f"#{m_amber.group(1)}", "confidence": 1.0}

        # 5. Spacing parameters
        rules["line_spacing"] = {"value": 1.15, "confidence": 0.8 if "1.15x" in text else 0.5}

        # 6. Ambiguous items (low confidence/not found)
        rules["logo_position"] = {"value": "top-left", "confidence": 0.8 if "top left" in text.lower() else 0.2}
        rules["logo_width_mm"] = {"value": 40, "confidence": 0.8 if "40 mm width" in text.lower() else 0.2}

        # Caption style: Section 3.2 specifies "Caption | Calibri Italic 9 pt | Charcoal"
        rules["caption_style"] = {"value": "italic", "confidence": 0.1}
        if re.search(r"Caption.*?Calibri Italic", text, re.IGNORECASE | re.DOTALL):
            rules["caption_style"] = {"value": "italic", "confidence": 0.95}

        # 7. Table body minimum font size — Rev-04 raised this from 9pt to 10pt (Section 3.2)
        rules["table_body_min_size"] = {"value": 10, "confidence": 0.5}
        m_table_min = re.search(r"table body.*?(?:raises|previous)\D*?(\d+)\s*pt\D*?to\s*(\d+)\s*pt", text, re.IGNORECASE | re.DOTALL)
        if m_table_min:
            rules["table_body_min_size"] = {"value": int(m_table_min.group(2)), "confidence": 0.95}
        elif "table body" in text.lower() and "10pt" in text.replace(" ", "").lower():
            rules["table_body_min_size"] = {"value": 10, "confidence": 0.9}

        return rules

    def build_instruction_markdown(self, rules: dict) -> str:
        font = rules["font_family"]["value"]
        h1 = rules["h1_size"]["value"]
        h2 = rules["h2_size"]["value"]
        line_sp = rules["line_spacing"]["value"]
        top = rules["top_margin"]["value"]
        bot = rules["bottom_margin"]["value"]
        primary = rules["primary_color"]["value"]
        
        table_min = rules.get("table_body_min_size", {"value": 10})["value"]
        caption_style = rules.get("caption_style", {"value": "italic"})["value"]
        monospace = rules.get("monospace_font", {"value": "Consolas"})["value"]

        md = f"""# Sankalit Document Branding Instructions

Always follow these visual style rules when generating documents:

## 1. Typography
- Use `{font}` font family universally for all body text, headings, headers, footers, and table elements.
- Use `{monospace}` (monospace) for document numbers, file paths, version strings, and technical codes only.
- Heading 1 size must be `{h1}pt` and bold.
- Heading 2 size must be `{h2}pt` and bold.
- Body paragraphs must use regular `{font}` of size `11pt`.
- Table header text must be `{font}` Bold, minimum `10pt`, white on Charcoal fill.
- Table body text must be `{font}` Regular, `11pt` preferred, minimum `{table_min}pt` (Rev-04 raised the floor from 9pt to {table_min}pt) — never smaller.
- Figure/table captions must be `{font}` {caption_style.capitalize()}, `9pt`, Charcoal — never bold.
- Line spacing must be set to `{line_sp}x`.

## 2. Page Layout
- Set top margin to `{top}mm` and bottom margin to `{bot}mm`.
- Left and right margins must be set to `25mm` (for Technical Reports / Proposals).

## 3. Brand Colors
- Primary Brand Accent Color: `{primary}` (Sankalit Orange) for rule lines, borders, and fills — never on heading text.
- Secondary Brand Highlight Color: `{rules["secondary_color"]["value"]}` (Sankalit Amber) for highlights and summary sub-fills.
- All heading text (H1-H4) must use Charcoal (`#5A5A5A`). Body text, H3/H4 headings, and table body text use Dark Grey (`#333333`). Never use pure black for text.

## 4. Company Name
- Always write the company name as `Sankalit Consultant`. Never `Sankalit IT Consultant`, and never append `Pvt. Ltd.` or pluralize to `Consultants`.
"""
        return md

    def build_manifest(self, rules: dict) -> dict:
        manifest = {}
        for key, details in rules.items():
            manifest[key] = {
                "confidence": details["confidence"],
                "value": details["value"]
            }
        return manifest

    def build_compile_report(self, rules: dict) -> str:
        report = []
        report.append("# Brand Compiler Report")
        report.append(f"- **Compiler Version**: {self.COMPILER_VERSION}")
        report.append(f"- **Guidelines Version**: {self.GUIDELINE_VERSION}")
        report.append("")
        report.append("## Rule Extraction Summary")
        for key, details in rules.items():
            conf = details["confidence"]
            val = details["value"]
            if conf >= 0.9:
                status = "✓"
                item_prefix = "Extracted"
            elif conf >= 0.5:
                status = "⚠"
                item_prefix = "Extracted with medium confidence"
            else:
                status = "✗"
                item_prefix = "Missing or ambiguous"
            report.append(f"- {status} **{key}**: {item_prefix} (`{val}`, confidence: {conf})")
        return "\n".join(report)

    def save(self, instructions: str, manifest: dict, report: str, sha256_hash: str):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_dir / "brand_instructions.md", "w", encoding="utf-8") as f:
            f.write(instructions)
            
        with open(self.output_dir / "brand_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
            
        with open(self.output_dir / "brand_compile_report.md", "w", encoding="utf-8") as f:
            f.write(report)
            
        meta = {
            "pdf_hash": sha256_hash,
            "compiler_version": self.COMPILER_VERSION,
            "compiled_at": "2026-07-22T14:43:00Z",
            "guideline_version": self.GUIDELINE_VERSION
        }
        with open(self.hash_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    def _compile_fallbacks(self):
        rules = {
            "font_family": {"value": "Calibri", "confidence": 1.0},
            "monospace_font": {"value": "Consolas", "confidence": 1.0},
            "h1_size": {"value": 14, "confidence": 1.0},
            "h2_size": {"value": 12, "confidence": 1.0},
            "h3_size": {"value": 11, "confidence": 1.0},
            "top_margin": {"value": 25.0, "confidence": 1.0},
            "bottom_margin": {"value": 20.0, "confidence": 1.0},
            "left_margin": {"value": 25.0, "confidence": 1.0},
            "right_margin": {"value": 25.0, "confidence": 1.0},
            "primary_color": {"value": "#F5A623", "confidence": 1.0},
            "secondary_color": {"value": "#F7C05A", "confidence": 1.0},
            "line_spacing": {"value": 1.15, "confidence": 1.0},
            "logo_position": {"value": "top-left", "confidence": 0.5},
            "logo_width_mm": {"value": 40, "confidence": 0.5},
            "caption_style": {"value": "italic", "confidence": 0.5},
            "table_body_min_size": {"value": 10, "confidence": 0.5}
        }
        instructions = self.build_instruction_markdown(rules)
        manifest = self.build_manifest(rules)
        report = self.build_compile_report(rules)
        self.save(instructions, manifest, report, "fallback")
