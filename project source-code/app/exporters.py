"""
PDF exporter for ComicCraft using ReportLab.
Produces a comic-book styled printable PDF with panel borders, badges,
dialogue speech bubbles, and captions matching the web interface.
"""

import os
import uuid
from pathlib import Path
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image as RLImage,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.layout_builder import ComicData, PanelData

EXPORTS_DIR = Path("static/exports")
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def export_comic_to_pdf(comic: ComicData) -> str:
    """
    Creates a comic-style PDF where every panel is arranged as:

        IMAGE
        PANEL HEADING
        STORY / NARRATION
        CAPTION

    Dialogue is shown in the image area where possible.
    """

    filename = f"comiccraft_{uuid.uuid4().hex[:8]}.pdf"
    file_path = EXPORTS_DIR / filename

    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ComicTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#d12f2f"),
        alignment=1,
        spaceAfter=6,
    )

    meta_style = ParagraphStyle(
        "ComicMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#666666"),
        alignment=1,
        spaceAfter=12,
    )

    panel_heading_style = ParagraphStyle(
        "PanelHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-BoldOblique",
        fontSize=12,
        leading=14,
        textColor=colors.HexColor("#111111"),
    )

    narration_style = ParagraphStyle(
        "PanelNarration",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=colors.white,
    )

    caption_style = ParagraphStyle(
        "PanelCaption",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#222222"),
    )

    story.append(
        Paragraph(
            f"COMICCRAFT: {comic.title.upper()}",
            title_style,
        )
    )

    story.append(
        Paragraph(
            f"Tone: {comic.tone} | "
            f"Art Style: {comic.art_style} | "
            f"5-Panel Storyboard",
            meta_style,
        )
    )

    for idx, panel in enumerate(comic.panels):
        panel_num = idx + 1

        elements = []

        # Image
        img_element = None

        if panel.image_url:
            local_img = panel.image_url.lstrip("/")

            if os.path.exists(local_img):
                try:
                    img_element = RLImage(
                        local_img,
                        width=500,
                        height=330,
                    )
                except Exception:
                    img_element = None

        if img_element:
            elements.append(img_element)
        else:
            elements.append(
                Paragraph(
                    f"[Panel {panel_num} image unavailable]",
                    meta_style,
                )
            )

        # Heading
        heading = (
            panel.panel_heading
            if getattr(panel, "panel_heading", "")
            else f"SCENE {panel_num}"
        )

        heading_table = Table(
            [
                [
                    Paragraph(
                        heading.upper(),
                        panel_heading_style,
                    )
                ]
            ],
            colWidths=[500],
        )

        heading_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.white,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        1.5,
                        colors.HexColor("#1f1b16"),
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        elements.append(heading_table)

        # Main narration
        narration = panel.scene_description or ""

        narration_table = Table(
            [
                [
                    Paragraph(
                        narration,
                        narration_style,
                    )
                ]
            ],
            colWidths=[500],
        )

        narration_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.black,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                ]
            )
        )

        elements.append(narration_table)

        # Bottom caption
        if panel.caption:
            caption_table = Table(
                [
                    [
                        Paragraph(
                            panel.caption.upper(),
                            caption_style,
                        )
                    ]
                ],
                colWidths=[500],
            )

            caption_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            colors.HexColor("#f4f1eb"),
                        ),
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            10,
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            10,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            7,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                    ]
                )
            )

            elements.append(caption_table)

        panel_table = Table(
            [[elements]],
            colWidths=[500],
        )

        panel_table.setStyle(
            TableStyle(
                [
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        2,
                        colors.HexColor("#1f1b16"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                ]
            )
        )

        story.append(panel_table)
        story.append(Spacer(1, 14))

    doc.build(story)

    return f"/static/exports/{filename}"
