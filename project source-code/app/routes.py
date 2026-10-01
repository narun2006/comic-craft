"""
API and HTML Route handlers for ComicCraft FastAPI application.
"""
import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates

from app.layout_builder import StoryRequest, ImageGenRequest, ComicData, PdfExportRequest
from app.gemini_flash import generate_comic_script
from app.gemini_pro import refine_comic_narrative
from app.image_generator import generate_panel_image
from app.exporters import export_comic_to_pdf

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

TONES = ["Funny", "Adventurous", "Dark", "Heartwarming", "Sci-Fi", "Mystery", "Epic"]
ART_STYLES = [
    "Classic Comic Book",
    "Manga",
    "Watercolor",
    "Pixel Art",
    "Noir",
    "Cartoon",
    "Retro Pop Art"
]


@router.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    """Renders the main interactive ComicCraft interface."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "tones": TONES,
            "art_styles": ART_STYLES
        }
    )


@router.post("/generate-comic")
async def generate_comic_endpoint(request: StoryRequest):
    """
    Generates a 5-panel comic story and prompts based on user input.
    Returns ComicData JSON.
    """
    try:
        comic = generate_comic_script(request)
        return comic.model_dump()
    except Exception as e:
        logger.error(f"Error generating comic: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-image")
async def generate_image_endpoint(req: ImageGenRequest):
    """
    Generates one panel image using Hugging Face Inference Providers.
    Returns image URL.
    """
    try:
        image_url = generate_panel_image(
            image_prompt=req.image_prompt,
            art_style=req.art_style,
            panel_number=req.panel_number
        )
        return {"image_url": image_url}
    except Exception as e:
        logger.error(f"Error generating panel image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download-pdf")
async def download_pdf_endpoint(req: PdfExportRequest):
    """
    Builds the ReportLab PDF for the generated comic.
    Returns the downloadable URL.
    """
    try:
        comic = ComicData(
            title=req.title,
            panels=req.panels,
            tone="Adventure",
            art_style=req.art_style
        )
        pdf_url = export_comic_to_pdf(comic)
        return {"pdf_url": pdf_url}
    except Exception as e:
        logger.error(f"Error creating PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comic-preview", response_class=HTMLResponse)
async def comic_preview_page(request: Request):
    """Preview route for viewing comics standalone."""
    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={}
    )


@router.get("/export-success", response_class=HTMLResponse)
async def export_success_page(request: Request, pdf: str = ""):
    """Export success page linking to generated PDF."""
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"pdf_url": pdf}
    )
