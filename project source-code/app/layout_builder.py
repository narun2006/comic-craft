"""
Layout builder and data models for ComicCraft.
Handles comic structure, panel definitions, request validation,
and data passed between the FastAPI routes and frontend.
"""

from typing import List, Optional

try:
    from pydantic import BaseModel, Field
except ImportError:
    # Lightweight fallback only for environments where Pydantic
    # has not been installed yet. The normal project should use Pydantic.
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

        def model_dump(self):
            result = {}
            for key, value in self.__dict__.items():
                if isinstance(value, list):
                    result[key] = [
                        item.model_dump() if hasattr(item, "model_dump") else item
                        for item in value
                    ]
                else:
                    result[key] = value
            return result

        def model_dump_json(self, indent=2):
            import json

            return json.dumps(self.model_dump(), indent=indent)

    def Field(default=None, default_factory=None, **kwargs):
        if default_factory is not None:
            return default_factory()
        return default


class StoryRequest(BaseModel):
    """Input sent by the user to create a new comic."""

    prompt: str = ""
    character: str = ""
    setting: str = ""
    tone: str = "Funny"
    art_style: str = "Classic Comic Book"


class PanelData(BaseModel):
    """Data for one comic panel."""

    panel_number: int = 1

    # Short title displayed directly below the image.
    panel_heading: str = ""

    # Main story/narration shown below the heading.
    scene_description: str = ""

    # Additional visual information used when building image prompts.
    character_action: str = ""
    character_expression: str = ""

    # Dialogue is rendered as a speech bubble by the frontend.
    dialogue: str = ""

    # Short dramatic caption displayed at the bottom.
    caption: str = ""

    # Prompt sent to Stable Diffusion XL.
    image_prompt: str = ""

    # Relative URL of the generated panel image.
    image_url: Optional[str] = None

    # True when image generation failed.
    failed: bool = False


class ComicData(BaseModel):
    """Complete generated comic."""

    title: str = ""
    panels: List[PanelData] = Field(default_factory=list)
    tone: str = "Funny"
    art_style: str = "Classic Comic Book"


class ImageGenRequest(BaseModel):
    """Request used by the image-generation endpoint."""

    image_prompt: str = ""
    art_style: str = "Classic Comic Book"
    panel_number: int = 1
    comic_id: Optional[str] = "default"


class PdfExportRequest(BaseModel):
    """Request used by the PDF export endpoint."""

    title: str = ""
    panels: List[PanelData] = Field(default_factory=list)
    art_style: str = "Classic Comic Book"
