from sankalit_mcp.styles.style_config import (
    StyleConfig,
    DocumentSection,
    FontsSection,
    TextFormat,
    TypographySection,
    ColorsSection,
    TablesSection,
    HeaderFooterSection,
    WatermarkSection,
)


class SankalitStyle:

    @staticmethod
    def get() -> StyleConfig:
        from sankalit_mcp.services.brand.brand_cache import BrandCache
        manifest = BrandCache.load_manifest()

        def get_val(key, default):
            if key in manifest:
                return manifest[key]["value"]
            return default

        top_margin = get_val("top_margin", 25.0)
        bottom_margin = get_val("bottom_margin", 20.0)
        left_margin = get_val("left_margin", 25.0)
        right_margin = get_val("right_margin", 25.0)

        font_family = get_val("font_family", "Calibri")
        monospace_font = get_val("monospace_font", "Consolas")

        h1_size = get_val("h1_size", 14)
        h2_size = get_val("h2_size", 12)
        h3_size = get_val("h3_size", 11)

        primary_color = get_val("primary_color", "#F5A623")
        secondary_color = get_val("secondary_color", "#F7C05A")

        return StyleConfig(
            document=DocumentSection(
                page_size="A4",
                orientation="portrait",
                margins={
                    "top": top_margin,
                    "bottom": bottom_margin,
                    "left": left_margin,
                    "right": right_margin,
                },
            ),
            fonts=FontsSection(
                font_family=font_family,
                fallback_font="Arial",
                monospace_font=monospace_font,
            ),
            typography=TypographySection(
                title=TextFormat(size=28, bold=True, color="#5A5A5A"),
                h1=TextFormat(size=h1_size, bold=True, color="#5A5A5A"),
                h2=TextFormat(size=h2_size, bold=True, color="#5A5A5A"),
                h3=TextFormat(size=h3_size, bold=True, color="#333333"),
                h4=TextFormat(size=h3_size, bold=True, italic=True, color="#333333"),
                body=TextFormat(size=11, color="#333333"),
                caption=TextFormat(size=9, italic=True, color="#5A5A5A"),
                footer=TextFormat(size=8, color="#5A5A5A"),
            ),
            colors=ColorsSection(
                primary=primary_color,
                secondary=secondary_color,
                charcoal="#5A5A5A",
                dark_grey="#333333",
                silver="#CCCCCC",
                white="#FFFFFF",
            ),
            tables=TablesSection(
                header_color="#5A5A5A",
                alternating_rows=True,
                border_color="#CCCCCC",
            ),
            header_footer=HeaderFooterSection(
                logo_variant="Variant 2",
                footer_text="Private & Confidential",
                page_numbers=True,
            ),
            watermark=WatermarkSection(
                enabled=True,
                text="DRAFT",
                color="#C8C8C8",
            ),
        )
