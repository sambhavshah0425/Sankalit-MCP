from dataclasses import dataclass, field
from typing import Dict


@dataclass
class DocumentSection:
    page_size: str = "A4"
    orientation: str = "portrait"
    margins: Dict[str, float] = field(default_factory=lambda: {
        "top": 2.54,
        "bottom": 2.54,
        "left": 2.54,
        "right": 2.54
    })


@dataclass
class FontsSection:
    font_family: str = "Arial"
    fallback_font: str = "Helvetica"
    monospace_font: str = "Courier New"


@dataclass
class TextFormat:
    size: int
    bold: bool = False
    italic: bool = False
    color: str = "black"


@dataclass
class TypographySection:
    title: TextFormat = field(default_factory=lambda: TextFormat(size=24, bold=True))
    h1: TextFormat = field(default_factory=lambda: TextFormat(size=18, bold=True))
    h2: TextFormat = field(default_factory=lambda: TextFormat(size=14, bold=True))
    h3: TextFormat = field(default_factory=lambda: TextFormat(size=12, bold=True))
    h4: TextFormat = field(default_factory=lambda: TextFormat(size=10, bold=True))
    body: TextFormat = field(default_factory=lambda: TextFormat(size=11))
    caption: TextFormat = field(default_factory=lambda: TextFormat(size=9, italic=True))
    footer: TextFormat = field(default_factory=lambda: TextFormat(size=8))


@dataclass
class ColorsSection:
    primary: str = "#000000"
    secondary: str = "#555555"
    charcoal: str = "#333333"
    dark_grey: str = "#666666"
    silver: str = "#CCCCCC"
    white: str = "#FFFFFF"


@dataclass
class TablesSection:
    header_color: str = "#000000"
    alternating_rows: bool = True
    border_color: str = "#CCCCCC"


@dataclass
class HeaderFooterSection:
    logo_variant: str = "default"
    footer_text: str = ""
    page_numbers: bool = True


@dataclass
class WatermarkSection:
    enabled: bool = False
    text: str = ""
    color: str = "#CCCCCC"


@dataclass
class StyleConfig:
    document: DocumentSection = field(default_factory=DocumentSection)
    fonts: FontsSection = field(default_factory=FontsSection)
    typography: TypographySection = field(default_factory=TypographySection)
    colors: ColorsSection = field(default_factory=ColorsSection)
    tables: TablesSection = field(default_factory=TablesSection)
    header_footer: HeaderFooterSection = field(default_factory=HeaderFooterSection)
    watermark: WatermarkSection = field(default_factory=WatermarkSection)

    @property
    def font_family(self) -> str:
        return self.fonts.font_family

    @property
    def h1_size(self) -> int:
        return self.typography.h1.size

    @property
    def page_size(self) -> str:
        return self.document.page_size
