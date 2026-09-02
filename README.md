# MindTrace

**Diagnosing how students think, not just what they get wrong.**

MindTrace is an AI-powered educational diagnostic tool. When a student explains a concept in their own words, MindTrace identifies the specific documented misconception behind their reasoning — with quoted evidence from their own writing and a targeted correction.

## Quick start (from project root)

```bash
# 1. Create env
cp backend/.env.example backend/.env
# Edit backend/.env and add your ANTHROPIC_API_KEY

# 2. Python env
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r backend/requirements.txt

# 3. Run
uvicorn backend.app.main:app --reload
```

Open http://localhost:8000

## Current status
- Scaffold complete (FastAPI + placeholder UI)
- No misconception KB, retrieval, or LLM calls yet
- Demo mode flag ready in .env (USE_CACHED_RESPONSES)

## Demo mode
Set `USE_CACHED_RESPONSES=true` in `backend/.env` once the diagnosis pipeline is built.

## Deploy
One-click deploy configs will be added (fly.toml / render.yaml).

## License
Hackathon project.
