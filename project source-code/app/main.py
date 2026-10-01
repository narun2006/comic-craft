"""
ComicCraft - AI Comic Story Creator
FastAPI Application Entry Point.
"""
import os
import uvicorn
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

from app.routes import router

app = FastAPI(
    title="ComicCraft",
    description="AI Comic Story Creator with FastAPI, Hugging Face and ReportLab",
    version="1.0.0"
)

# CORS middleware for seamless API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static folders exist
for folder in ["static", "static/panels", "static/exports", "static/fonts"]:
    Path(folder).mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routes
app.include_router(router)


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    print(f"🚀 Starting ComicCraft on http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=debug)
