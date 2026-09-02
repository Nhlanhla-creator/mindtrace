from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="MindTrace", description="Diagnosing how students think, not just what they get wrong.")

# Mount static if present (for future frontend assets)
static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MindTrace • Scaffold</title>
  <style>
    :root {
      --bg: #15152B;
      --surface: #1F1F3D;
      --amber: #F5A623;
      --violet: #8C7AE6;
      --text: #F4F4F8;
      --muted: #9291B5;
    }
    body { margin:0; background:var(--bg); color:var(--text); font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }
    .container { max-width: 860px; margin: 0 auto; padding: 48px 24px; }
    header { display:flex; align-items:center; gap:12px; margin-bottom:32px; }
    .logo { width:42px; height:42px; background: linear-gradient(135deg, var(--amber), var(--violet)); border-radius:8px; }
    h1 { font-family: Georgia, Cambria, serif; font-size: 2.25rem; margin:0; }
    .tagline { color: var(--muted); font-size:1.05rem; margin-top:4px; }
    .card {
      background: var(--surface);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 20px;
      border: 1px solid rgba(255,255,255,0.06);
    }
    .status { display:inline-flex; align-items:center; gap:8px; padding:6px 12px; background:#2A2A52; border-radius:999px; font-size:0.9rem; }
    .dot { width:8px; height:8px; background:#4ADE80; border-radius:50%; display:inline-block; }
    pre { background:#11111f; padding:12px; border-radius:8px; overflow:auto; font-size:0.85rem; color:#c8c7e0; }
    .note { color:var(--muted); font-size:0.9rem; }
    .actions a { color:var(--amber); text-decoration:none; }
    .actions a:hover { text-decoration:underline; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo"></div>
      <div>
        <h1>MindTrace</h1>
        <div class="tagline">Diagnosing how students think, not just what they get wrong.</div>
      </div>
    </header>

    <div class="card">
      <div class="status"><span class="dot"></span> Backend running • scaffold stage</div>
      <h2 style="margin:16px 0 8px 0; font-family:Georgia,serif;">Current state</h2>
      <p>This is the initial scaffold. The full pipeline (knowledge base, TF-IDF retrieval, Claude confirmation, profile, multi-modal, etc.) is not yet wired.</p>
      <p class="note">Next: misconception knowledge base (25 entries) → retrieval → API integration → frontend.</p>
    </div>

    <div class="card">
      <h3 style="margin-top:0;">Quick checks</h3>
      <ul>
        <li><a href="/health">/health</a> — JSON health endpoint</li>
        <li>Repo: <a href="https://github.com/Nhlanhla-creator/mindtrace" target="_blank">github.com/Nhlanhla-creator/mindtrace</a></li>
      </ul>
      <p class="note">Run with: <code>uvicorn backend.app.main:app --reload</code> from project root.</p>
    </div>

    <div class="actions">
      <a href="https://github.com/Nhlanhla-creator/mindtrace">View on GitHub →</a>
    </div>
  </div>
</body>
</html>
    """
    return html

@app.get("/health")
def health():
    return JSONResponse({"status": "ok", "service": "mindtrace", "stage": "scaffold"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
