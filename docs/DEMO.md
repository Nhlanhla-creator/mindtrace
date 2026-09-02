# MindTrace demo notes

## Run locally

```powershell
cd C:\Users\nhlan\mindtrace
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
# Set ANTHROPIC_API_KEY for live confirmation, or USE_CACHED_RESPONSES=true for recording.
python -m uvicorn backend.app.main:app --reload
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Demo path

1. Click **Heavier falls faster**. Confirm the violet misconception, amber quote, research fix, and retrieval bars.
2. Click **Force sustains motion**. The diagnosis changes while the profile records both patterns.
3. Click **Compare** and enter the first two physics examples side by side.
4. Click **Speak** in Chrome or Edge and allow microphone access.
5. Upload a clear handwritten image. Local Tesseract OCR extracts text, then press Analyze.
6. Click **Library** to browse all 25 knowledge-base entries.
7. Click **Copy shareable link**, open it in a new tab, and submit the restored explanation.
8. Enter a room ID in two tabs to verify collaboration messages.

## Verification

```powershell
$env:PYTHONPATH='C:\Users\nhlan\mindtrace'
python -m pytest tests -q
python -m compileall -q backend
node --check frontend\static\js\app.js
```

The backend falls back to deterministic retrieval when Claude is unavailable. Cached responses are only used when `USE_CACHED_RESPONSES=true`.
