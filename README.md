# ComicCraft AI 🎨

> **Turn any story idea into a complete illustrated comic — instantly.**

ComicCraft AI is a full-stack AI comic story creator that transforms a user's story idea into a structured **5-panel comic** with AI-written storytelling, consistent character descriptions, generated artwork, dialogue, captions, and a downloadable PDF storyboard.

The application is designed so users can provide completely different stories, characters, settings, tones, and visual styles without being restricted to a predefined example.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📝 Any story prompt | Enter any original story idea in natural language |
| 👤 Character input | Define the main character and maintain visual continuity |
| 🌍 Custom setting | Specify where the story takes place |
| 🎭 Story tone | Choose the tone of the generated story |
| 🎨 Art style | Choose the visual style for generated panels |
| 📖 5-panel story | Generates a connected beginning-to-ending comic |
| 🏷️ Panel headings | Each panel receives a short dramatic scene heading |
| 💬 Dialogue bubbles | Dialogue is rendered separately over the image |
| 🖼️ AI artwork | Stable Diffusion XL generates the panel artwork |
| 📚 Story narration | Each panel contains narrative text beneath the image |
| 🏷️ Captions | Short dramatic captions are displayed below the narration |
| 🔄 Panel redraw | Individual panels can be regenerated |
| 📄 PDF export | Download the completed comic as a storyboard PDF |
| 📱 Responsive UI | Comic layout adapts to desktop and smaller screens |
| 🔐 API key protection | API keys remain in the backend `.env` file |

---

# 🧠 How It Works

ComicCraft uses a two-stage AI generation pipeline followed by PDF assembly.

```text
                    USER
                      │
                      ▼
             Story + Character
             + Setting + Tone
             + Art Style
                      │
                      ▼
       ┌────────────────────────────┐
       │     Gemini 3.8 Flash       │
       │                            │
       │  Story + Comic Script      │
       │  Character Continuity      │
       │  Panel Headings            │
       │  Dialogue + Captions       │
       │  Image Prompts             │
       └──────────────┬─────────────┘
                      │
                      ▼
              Five Panel Prompts
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
       Panel 1                 Panel 2
          │                       │
          └───────────┬───────────┘
                      │
                     ...
                      │
                      ▼
       ┌────────────────────────────┐
       │  Stable Diffusion XL 1.0   │
       │     Stability AI API       │
       │                            │
       │  Text → Comic Artwork      │
       └──────────────┬─────────────┘
                      │
                      ▼
             Generated PNG Panels
                      │
                      ▼
       ┌────────────────────────────┐
       │       ComicCraft UI        │
       │                            │
       │ Image                      │
       │ Panel Heading              │
       │ Narration                  │
       │ Caption                    │
       │ Dialogue Bubble            │
       └──────────────┬─────────────┘
                      │
                      ▼
       ┌────────────────────────────┐
       │         ReportLab          │
       │                            │
       │       PDF Storyboard       │
       └────────────────────────────┘
```

---

# 🤖 AI Pipeline

## Stage 1 — Story and Comic Script Generation

ComicCraft uses **Gemini 3.8 Flash** for the story generation stage.

Gemini receives:

```text
User Story
Main Character
Setting
Story Tone
Art Style
```

It generates:

```text
Comic Title
      │
      ├── Panel 1
      ├── Panel 2
      ├── Panel 3
      ├── Panel 4
      └── Panel 5
```

Each panel contains:

```text
Panel Number
Panel Heading
Scene Description
Character Action
Character Expression
Dialogue
Caption
Image Prompt
```

The application uses structured JSON output through Pydantic models so the backend receives predictable comic data instead of relying on free-form text parsing.

---

# 🎨 Stage 2 — AI Image Generation

ComicCraft sends the image prompt for each panel to **Stable Diffusion XL 1.0 through the Stability AI API**.

Current engine:

```text
stable-diffusion-xl-1024-v1-0
```

The image prompt contains:

- Character appearance
- Character action
- Character expression
- Setting
- Composition
- Camera framing
- Lighting
- Art style
- Visual continuity instructions

The prompt explicitly requests:

```text
No text
No letters
No words
No speech bubbles
No captions
No watermark
No logo
```

This is intentional.

ComicCraft does **not** ask Stable Diffusion to render readable dialogue inside the image. Instead, the web application renders dialogue bubbles over the generated artwork, giving much better control over readable text.

---

# 💬 Comic Panel Layout

The generated result is presented in a comic-card layout:

```text
┌──────────────────────────────┐
│ 1                            │
│                              │
│       AI GENERATED IMAGE     │
│                              │
│                  "Dialogue"  │
│                              │
├──────────────────────────────┤
│ A CURIOUS WANDERER           │
├──────────────────────────────┤
│ The forest was full of       │
│ secrets and strange sounds.  │
├──────────────────────────────┤
│ DEEP WITHIN THE FOREST...    │
├──────────────────────────────┤
│ 🔄 Redraw                    │
└──────────────────────────────┘
```

This separates:

```text
AI artwork
      +
Story narration
      +
Dialogue
      +
Captions
```

instead of attempting to generate all comic text inside the image model.

---

# 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| AI Story Generation | Gemini 3.8 Flash | Story, panels, dialogue, captions and image prompts |
| AI Image Generation | Stable Diffusion XL 1.0 | Comic panel artwork |
| Image Provider | Stability AI API | Direct SDXL image generation |
| Backend | Python | Application logic |
| API Framework | FastAPI | REST endpoints and page serving |
| Server | Uvicorn | Local ASGI server |
| Validation | Pydantic | Structured request/response models |
| PDF | ReportLab | Comic storyboard export |
| Image Processing | Pillow | Image handling and validation |
| Frontend | HTML5 | User interface |
| Styling | CSS | Comic-style responsive interface |
| Client Logic | Vanilla JavaScript | API requests, rendering and redraw |
| Templates | Jinja2 | Server-side HTML rendering |

---

# 📁 Project Structure

```text
comiccraft/
│
├── app/
│   ├── main.py
│   │   └── FastAPI application entry point
│   │
│   ├── routes.py
│   │   └── Application API and page routes
│   │
│   ├── layout_builder.py
│   │   └── Pydantic request and comic data models
│   │
│   ├── gemini_flash.py
│   │   └── Gemini story/script generation
│   │
│   ├── image_generator.py
│   │   └── Stable Diffusion XL image generation
│   │
│   └── exporters.py
│       └── ReportLab PDF generation
│
├── templates/
│   └── index.html
│       └── Main ComicCraft interface
│
├── static/
│   ├── panels/
│   │   └── Generated comic panel images
│   │
│   └── exports/
│       └── Generated PDF files
│
├── .env.example
│   └── Environment variable template
│
├── .gitignore
├── requirements.txt
├── README.md
└── LICENSE
```

---

# ⚙️ Requirements

Before running ComicCraft, install:

```text
Python 3.10+
```

The application does **not require Node.js or npm** because the frontend is served directly by FastAPI.

You also need:

```text
Google Gemini API key
Stability AI API key
```

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd comiccraft
```

---

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell activation is unavailable, you can use:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

---

# 🔑 API Configuration

Create:

```text
.env
```

in the project root.

Use:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash

STABILITY_API_KEY=your_stability_api_key
STABILITY_MODEL=stable-diffusion-xl-1024-v1-0

HOST=127.0.0.1
PORT=8000
DEBUG=True
```

### Important

Never commit:

```text
.env
```

to GitHub.

Commit only:

```text
.env.example
```

---

# ▶️ Run Locally

Start the FastAPI server:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

# 🧪 Example Prompt

### Story Prompt

```text
A young girl discovers a tiny dragon living inside an old
library book. She tries to keep it secret, but its magic
accidentally brings the entire library to life.
```

### Main Character

```text
Maya, a curious 12-year-old girl wearing round glasses
```

### Setting

```text
An ancient magical library
```

### Tone

```text
Fantasy
```

### Art Style

```text
Classic Comic Book
```

ComicCraft will generate:

```text
Panel 1 → Story setup
Panel 2 → Discovery
Panel 3 → Magic begins
Panel 4 → Major conflict
Panel 5 → Resolution
```

---

# 🔄 Panel Redraw

Every panel includes a redraw option.

When the user clicks:

```text
🔄 Redraw
```

ComicCraft sends the same panel image prompt back to the Stable Diffusion XL generation endpoint.

Only that panel is regenerated.

The rest of the comic remains unchanged.

---

# 📄 PDF Export

After generating the comic, click:

```text
📥 Download PDF
```

ComicCraft creates a storyboard PDF using ReportLab.

The PDF contains:

```text
Comic Title
        ↓
Panel Image
        ↓
Panel Heading
        ↓
Story Narration
        ↓
Caption
```

This makes the exported result useful for:

- Storyboarding
- Classroom activities
- Creative writing
- Comic prototyping
- Educational material
- Character storytelling

---

# 🌍 Supported Story Types

ComicCraft is designed to work with arbitrary story prompts rather than a fixed story template.

Examples include:

```text
Fantasy
Adventure
Comedy
Horror
Mystery
Sci-Fi
Slice of Life
Children's stories
Fables
Moral stories
Historical fiction
Superhero stories
Animal stories
Travel stories
Educational stories
```

The application does not require the user to follow a predefined storyline.

---

# 🔐 Security

API keys should only exist in:

```text
.env
```

Never place API keys inside:

```text
HTML
JavaScript
CSS
GitHub repository
Frontend source
```

The browser communicates with FastAPI, and the backend communicates with Gemini and Stability AI.

Recommended `.gitignore`:

```gitignore
.venv/
__pycache__/
*.pyc
.env

static/panels/*
static/exports/*
```

You can use `.gitkeep` files if you want GitHub to preserve the empty directories:

```text
static/panels/.gitkeep
static/exports/.gitkeep
```

---

# 💰 API Usage

ComicCraft does not use Hugging Face Inference Providers.

The current architecture is:

```text
Gemini API
      +
Stability AI API
```

Gemini and Stability AI have their own usage limits, quotas, pricing and model availability. Check their current documentation before deploying the application publicly.

---

# 🧩 API Endpoints

The main application endpoints include:

```text
GET  /
POST /generate-comic
POST /generate-image
POST /download-pdf
```

FastAPI automatically exposes:

```text
/docs
```

for interactive API documentation.

---

# 🏗️ Application Flow

```text
1. User opens ComicCraft
             ↓
2. User enters story information
             ↓
3. POST /generate-comic
             ↓
4. Gemini generates the 5-panel script
             ↓
5. ComicCraft renders the panel cards
             ↓
6. Frontend requests each image sequentially
             ↓
7. POST /generate-image
             ↓
8. Stability AI generates the artwork
             ↓
9. Generated image appears in the panel
             ↓
10. Dialogue appears as a speech bubble
             ↓
11. User can redraw individual panels
             ↓
12. User downloads the complete PDF
```

---

# 🎯 Use Cases

### 🎓 Students

Turn assignments, essays, and creative writing into visual stories.

### ✏️ Writers

Visualize story concepts before creating a complete comic.

### 👩‍🏫 Teachers

Create comic-based educational material.

### 🎨 Indie Creators

Prototype comic ideas without manually drawing every panel.

### 📱 Content Creators

Create short visual stories for digital content.

### 🌍 Storytellers

Transform original stories, fables, and regional narratives into comics.

---

# 🔮 Future Improvements

Potential future improvements include:

```text
Character reference images
Character image consistency using reference conditioning
Multi-character story support
More image models
Multiple panel layouts
Comic page generation
Voice narration
Multilingual story generation
Custom speech-bubble positioning
Editable dialogue
Drag-and-drop panel ordering
Cloud storage
User accounts
Comic libraries
Social sharing
```

---

# 🛡️ Current Design Philosophy

ComicCraft deliberately separates **text generation** from **image generation**:

```text
Gemini
   ↓
Story + Dialogue + Narration
   ↓
Image Prompt
   ↓
Stable Diffusion XL
   ↓
Artwork only
   ↓
Frontend
   ↓
Speech Bubble + Text
```

This provides better control over readable comic text and allows the application to modify story presentation without regenerating the artwork.

---

# 📜 License

MIT License

You are free to:

- Use
- Modify
- Distribute
- Build upon

the project according to the terms of the MIT License.

---

# ❤️ ComicCraft

> **Every story deserves to be seen.**

ComicCraft combines generative storytelling, AI artwork, and comic-style layout into a single local web application.

**Gemini creates the story.  
Stable Diffusion creates the art.  
ComicCraft brings them together.**
