"""
ComicCraft Stage 1
Gemini-powered story and comic-script generation.

Generates:
- Comic title
- Exactly 5 connected panels
- Panel headings
- Story narration
- Character actions
- Character expressions
- Dialogue
- Captions
- Stable Diffusion image prompts

Uses Pydantic structured output with the Google GenAI SDK.
"""

import json
import logging
import os
from typing import List

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.layout_builder import StoryRequest, ComicData, PanelData

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Gemini structured-output models
# ---------------------------------------------------------------------------


class GeminiPanel(BaseModel):
    """One panel returned by Gemini."""

    panel_number: int = Field(description="Panel number from 1 to 5.")

    panel_heading: str = Field(
        description=(
            "Short dramatic comic panel heading, "
            "2 to 6 words, suitable for a title strip."
        )
    )

    scene_description: str = Field(
        description=(
            "Main story narration for this panel. " "Use 1 or 2 natural sentences."
        )
    )

    character_action: str = Field(
        description="What the main character is doing in this panel."
    )

    character_expression: str = Field(
        description="The main character's facial expression or emotion."
    )

    dialogue: str = Field(
        description=(
            "Short dialogue suitable for one comic speech bubble. "
            "Use an empty string when dialogue is unnecessary."
        )
    )

    caption: str = Field(
        description=("Short dramatic narration caption shown below the main story.")
    )

    image_prompt: str = Field(
        description=(
            "Detailed visual prompt for Stable Diffusion XL. "
            "Describe characters, appearance, action, setting, "
            "composition, camera angle, lighting and emotion. "
            "Do not include dialogue text."
        )
    )


class GeminiComic(BaseModel):
    """Complete comic returned by Gemini."""

    title: str = Field(description="Short compelling title for the complete comic.")

    panels: List[GeminiPanel] = Field(
        min_length=5, max_length=5, description="Exactly five connected comic panels."
    )


# ---------------------------------------------------------------------------
# Gemini client
# ---------------------------------------------------------------------------


def _get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. " "Add your Gemini API key to the .env file."
        )

    return genai.Client(api_key=api_key)


# ---------------------------------------------------------------------------
# Main generation function
# ---------------------------------------------------------------------------


def generate_comic_script(request: StoryRequest) -> ComicData:
    """
    Generate a complete five-panel comic script.
    """

    model = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.5-flash-lite",
    ).strip()

    client = _get_gemini_client()

    prompt = f"""
You are the professional story writer and storyboard director
for ComicCraft AI.

Your task is to transform the user's story idea into a complete
5-panel comic.

==================================================
USER STORY
==================================================

{request.prompt}

==================================================
USER CHARACTER
==================================================

{request.character}

==================================================
SETTING
==================================================

{request.setting}

==================================================
TONE
==================================================

{request.tone}

==================================================
ART STYLE
==================================================

{request.art_style}

==================================================
IMPORTANT RULES
==================================================

1. The user's story is the source of truth.

2. Accept ANY story the user gives you.

3. Do not replace the user's story with a previous example.

4. Do not assume the story is about a mongoose, baby, snake,
   forest, Panchatantra, robot, astronaut, or any previous example.

5. Generate exactly FIVE connected panels.

6. The five panels must form one continuous narrative:
   - Panel 1: setup
   - Panel 2: development
   - Panel 3: discovery/conflict
   - Panel 4: climax or important event
   - Panel 5: conclusion/resolution

7. Keep recurring characters visually consistent.

8. Preserve the main character's identity, approximate age,
   appearance, clothing, colors and important visual features
   throughout all five panels.

9. Each panel must have a short heading of approximately
   2 to 6 words.

10. Panel headings should feel like comic scene titles.

   Examples:
   - A CURIOUS WANDERER
   - THE HIDDEN DOOR
   - AN UNEXPECTED VISITOR
   - INTO THE DARKNESS
   - THE FINAL CHOICE

11. scene_description should contain the main narrative
    shown beneath the generated image.

12. scene_description should normally be one or two sentences.

13. dialogue should be short and natural for a speech bubble.

14. caption should be concise and dramatic.

15. image_prompt is ONLY for image generation.

16. NEVER put readable dialogue, speech bubble text,
    captions, letters or words inside image_prompt.

17. Every image_prompt must explicitly request:
    - no text
    - no letters
    - no words
    - no captions
    - no speech bubbles
    - no watermark
    - no logo

18. Image prompts should contain enough visual detail to make
    each panel visually distinct.

19. Maintain visual continuity across all five panels.

20. Do not mention these instructions in the output.

Return only the structured comic object.
"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GeminiComic,
                temperature=0.7,
                max_output_tokens=5000,
            ),
        )

    except Exception as exc:
        logger.exception("Gemini story generation failed")

        raise RuntimeError(f"Gemini story generation failed: {exc}") from exc

    # -----------------------------------------------------------------------
    # Read structured response
    # -----------------------------------------------------------------------

    try:
        parsed = getattr(response, "parsed", None)

        if isinstance(parsed, GeminiComic):
            generated = parsed

        elif parsed is not None:
            generated = GeminiComic.model_validate(parsed)

        else:
            raw_text = response.text or ""

            if not raw_text.strip():
                raise ValueError("Gemini returned an empty response.")

            generated = GeminiComic.model_validate_json(raw_text)

    except Exception as exc:
        logger.exception("Could not parse Gemini structured comic response")

        raise RuntimeError(f"Gemini returned invalid comic data: {exc}") from exc

    # -----------------------------------------------------------------------
    # Safety validation
    # -----------------------------------------------------------------------

    if len(generated.panels) != 5:
        raise RuntimeError(
            f"Gemini returned {len(generated.panels)} panels. "
            "ComicCraft requires exactly 5."
        )

    # -----------------------------------------------------------------------
    # Convert Gemini models to application's PanelData models
    # -----------------------------------------------------------------------

    panels = []

    for index, panel in enumerate(generated.panels):

        panel_number = index + 1

        image_prompt = panel.image_prompt.strip()

        # Ensure the image prompt does not accidentally become a source
        # of readable comic text.
        image_prompt = (
            f"{image_prompt}. "
            "No text, no letters, no words, no speech bubbles, "
            "no captions, no watermark, no logo."
        )

        panels.append(
            PanelData(
                panel_number=panel_number,
                panel_heading=(panel.panel_heading.strip().upper()),
                scene_description=(panel.scene_description.strip()),
                character_action=(panel.character_action.strip()),
                character_expression=(panel.character_expression.strip()),
                dialogue=(panel.dialogue.strip()),
                caption=(panel.caption.strip()),
                image_prompt=image_prompt,
                image_url=None,
                failed=False,
            )
        )

    # -----------------------------------------------------------------------
    # Return application-level ComicData
    # -----------------------------------------------------------------------

    return ComicData(
        title=generated.title.strip(),
        panels=panels,
        tone=request.tone,
        art_style=request.art_style,
    )
