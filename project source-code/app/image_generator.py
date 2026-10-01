"""
Stable Diffusion XL image generation for ComicCraft.

Stage 2:
- Takes each Gemini-generated image prompt.
- Sends it directly to Stability AI.
- Uses Stable Diffusion XL 1.0.
- Saves the generated PNG locally.
"""

import os
import uuid
import logging
import base64

from pathlib import Path

import requests
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)

STATIC_PANELS_DIR = Path("static/panels")
STATIC_PANELS_DIR.mkdir(parents=True, exist_ok=True)


STYLE_PRESETS = {
    "Classic Comic Book": "comic-book",
    "Manga": "anime",
    "Watercolor": "digital-art",
    "Pixel Art": "pixel-art",
    "Noir": "cinematic",
    "Cartoon": "digital-art",
    "Retro Pop Art": "comic-book",
}


def _create_placeholder_panel(
    panel_number: int,
    art_style: str,
    prompt: str,
    filename: str,
) -> str:
    """
    Optional local fallback.
    This is NOT an AI-generated image.
    """

    width, height = 1024, 1024

    bg = (245, 240, 230)

    img = Image.new(
        "RGB",
        (width, height),
        bg,
    )

    draw = ImageDraw.Draw(img)

    border = (20, 20, 20)

    draw.rectangle(
        [(12, 12), (width - 12, height - 12)],
        outline=border,
        width=8,
    )

    draw.text(
        (35, 35),
        f"PANEL {panel_number}",
        fill=border,
    )

    draw.text(
        (35, 75),
        "Stable Diffusion XL unavailable",
        fill=border,
    )

    summary = prompt[:250]

    if len(prompt) > 250:
        summary += "..."

    draw.multiline_text(
        (35, height - 220),
        summary,
        fill=border,
        spacing=6,
    )

    path = STATIC_PANELS_DIR / filename

    img.save(path, "PNG")

    return f"/static/panels/{filename}"


def generate_panel_image(
    image_prompt: str,
    art_style: str = "Classic Comic Book",
    panel_number: int = 1,
) -> str:

    api_key = os.getenv(
        "STABILITY_API_KEY",
        ""
    ).strip()

    if not api_key:
        raise ValueError(
            "STABILITY_API_KEY is not set. "
            "Add your Stability AI API key to .env."
        )

    model = os.getenv(
        "STABILITY_MODEL",
        "stable-diffusion-xl-1024-v1-0",
    ).strip()

    filename = (
        f"panel_{panel_number}_"
        f"{uuid.uuid4().hex[:8]}.png"
    )

    style_preset = STYLE_PRESETS.get(
        art_style,
        "comic-book",
    )

    full_prompt = (
        f"{image_prompt}. "
        "Create a single square comic panel. "
        "Strong visual storytelling. "
        "Consistent recurring character appearance. "
        "Clear facial expression and body language. "
        "Cinematic composition and lighting. "
        "No text, no letters, no words, "
        "no speech bubbles, no captions, "
        "no watermark."
    )

    negative_prompt = (
        "text, letters, words, subtitles, speech bubbles, "
        "captions, watermark, logo, signature, blurry, "
        "low quality, distorted anatomy, extra limbs, "
        "duplicate characters, malformed hands"
    )

    url = (
        "https://api.stability.ai/v1/generation/"
        f"{model}/text-to-image"
    )

    payload = {
        "steps": 30,
        "width": 1024,
        "height": 1024,
        "cfg_scale": 7,
        "samples": 1,
        "style_preset": style_preset,
        "text_prompts": [
            {
                "text": full_prompt,
                "weight": 1,
            },
            {
                "text": negative_prompt,
                "weight": -1,
            },
        ],
    }

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=180,
        )

        if not response.ok:
            try:
                error_payload = response.json()
            except Exception:
                error_payload = response.text

            raise RuntimeError(
                "Stable Diffusion XL API error "
                f"(HTTP {response.status_code}): "
                f"{error_payload}"
            )

        response_data = response.json()

        artifacts = response_data.get(
            "artifacts",
            [],
        )

        if not artifacts:
            raise RuntimeError(
                "Stable Diffusion XL returned no image artifacts."
            )

        image_data = artifacts[0].get(
            "base64"
        )

        if not image_data:
            raise RuntimeError(
                "Stable Diffusion XL returned an image "
                "without base64 data."
            )

        image_bytes = base64.b64decode(
            image_data
        )

        output_path = (
            STATIC_PANELS_DIR / filename
        )

        with open(
            output_path,
            "wb",
        ) as image_file:
            image_file.write(image_bytes)

        # Verify that the saved file is a valid image.
        with Image.open(output_path) as img:
            img.verify()

        logger.info(
            "Generated panel %s successfully",
            panel_number,
        )

        return f"/static/panels/{filename}"

    except Exception as exc:
        logger.exception(
            "Stable Diffusion XL image generation failed"
        )

        if (
            os.getenv(
                "ALLOW_IMAGE_PLACEHOLDER",
                "false"
            ).lower()
            == "true"
        ):
            return _create_placeholder_panel(
                panel_number,
                art_style,
                image_prompt,
                filename,
            )

        raise RuntimeError(
            f"Stable Diffusion XL image generation failed: {exc}"
        ) from exc