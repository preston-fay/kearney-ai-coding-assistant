# Presentation Slide Template
# KDS-Compliant PowerPoint Generation
#
# Usage:
#   from templates.presentation.slide_template import create_presentation
#   create_presentation(slides_data, output_path)

import sys
from pathlib import Path
from typing import Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.slide_engine import KDSPresentation


def create_title_slide(
    pres: KDSPresentation,
    title: str,
    subtitle: Optional[str] = None
) -> None:
    """Add a KDS-compliant title slide."""
    pres.add_title_slide(title, subtitle)


def create_content_slide(
    pres: KDSPresentation,
    title: str,
    bullet_points: list
) -> None:
    """Add a KDS-compliant content slide with bullet points."""
    pres.add_content_slide(title, bullet_points)


def create_chart_slide(
    pres: KDSPresentation,
    title: str,
    chart_path: Path
) -> None:
    """Add a slide with an embedded chart image."""
    pres.add_image_slide(title, str(chart_path))


def create_section_slide(
    pres: KDSPresentation,
    section_title: str
) -> None:
    """Add a section divider slide."""
    pres.add_section_slide(section_title)


def create_presentation(
    slides_data: list,
    output_path: Path,
    title: str = "Presentation",
    subtitle: Optional[str] = None
) -> Path:
    """
    Create a complete KDS-compliant presentation.

    Args:
        slides_data: List of slide definitions, each a dict with:
            - type: "title", "content", "chart", "section"
            - Additional fields based on type
        output_path: Where to save the PPTX
        title: Presentation title for title slide
        subtitle: Optional subtitle

    Example slides_data:
        [
            {"type": "content", "title": "Key Findings", "bullets": ["Point 1", "Point 2"]},
            {"type": "chart", "title": "Revenue Analysis", "chart_path": "charts/revenue.png"},
            {"type": "section", "title": "Recommendations"},
        ]

    Returns:
        Path to generated presentation
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pres = KDSPresentation()

    # Always start with title slide
    create_title_slide(pres, title, subtitle)

    # Process each slide
    for slide_def in slides_data:
        slide_type = slide_def.get("type", "content")

        if slide_type == "title":
            create_title_slide(
                pres,
                slide_def.get("title", ""),
                slide_def.get("subtitle")
            )
        elif slide_type == "content":
            create_content_slide(
                pres,
                slide_def.get("title", ""),
                slide_def.get("bullets", [])
            )
        elif slide_type == "chart":
            chart_path = slide_def.get("chart_path")
            if chart_path and Path(chart_path).exists():
                create_chart_slide(
                    pres,
                    slide_def.get("title", ""),
                    Path(chart_path)
                )
        elif slide_type == "section":
            create_section_slide(
                pres,
                slide_def.get("title", "")
            )

    pres.save(output_path)
    return output_path


def create_executive_summary(
    title: str,
    key_findings: list,
    recommendations: list,
    output_path: Path,
    chart_paths: Optional[list] = None
) -> Path:
    """
    Create a standard executive summary presentation.

    Args:
        title: Presentation title
        key_findings: List of key finding strings
        recommendations: List of recommendation strings
        output_path: Where to save
        chart_paths: Optional list of chart image paths

    Returns:
        Path to generated presentation
    """
    slides = []

    # Key Findings slide
    slides.append({
        "type": "content",
        "title": "Key Findings",
        "bullets": key_findings
    })

    # Chart slides if provided
    if chart_paths:
        slides.append({
            "type": "section",
            "title": "Analysis"
        })
        for i, chart_path in enumerate(chart_paths):
            slides.append({
                "type": "chart",
                "title": f"Analysis {i + 1}",
                "chart_path": str(chart_path)
            })

    # Recommendations
    slides.append({
        "type": "section",
        "title": "Recommendations"
    })
    slides.append({
        "type": "content",
        "title": "Recommendations",
        "bullets": recommendations
    })

    return create_presentation(
        slides,
        output_path,
        title=title,
        subtitle="Executive Summary"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate KDS presentation")
    parser.add_argument("--output", "-o", default="outputs/presentation.pptx", help="Output path")
    parser.add_argument("--title", "-t", default="Sample Presentation", help="Title")

    args = parser.parse_args()

    # Demo presentation
    slides = [
        {"type": "content", "title": "Overview", "bullets": [
            "This is a sample KDS-compliant presentation",
            "Generated using the Kearney AI Coding Assistant",
            "All styling follows brand guidelines"
        ]},
        {"type": "section", "title": "Details"},
        {"type": "content", "title": "Features", "bullets": [
            "Kearney Purple primary color",
            "Inter font family",
            "Dark mode support",
            "No forbidden colors or emojis"
        ]},
    ]

    output = create_presentation(
        slides,
        Path(args.output),
        title=args.title,
        subtitle="Demo"
    )
    print(f"Presentation created: {output}")
