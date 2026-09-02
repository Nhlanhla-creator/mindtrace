from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

from .diagnosis import diagnose
from .profile import Profile
from .retrieval import retriever

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(title="MindTrace", description="Diagnosing how students think, not just what they get wrong.")
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"
PROFILES: dict[str, Profile] = {}
ROOMS: dict[str, set[WebSocket]] = {}

if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ExplanationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    topic: str | None = None
    session_id: str | None = None
    limit: int = Field(default=5, ge=1, le=10)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("text must not be blank")
        return cleaned


class RoomRequest(BaseModel):
    room_id: str | None = None


@app.get("/", response_class=FileResponse)
def root():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/api/diagnose")
def diagnose_explanation(request: ExplanationRequest):
    result = diagnose(request.text, request.topic)
    session_id = request.session_id or str(uuid4())
    profile = PROFILES.setdefault(session_id, Profile())
    result["session_id"] = session_id
    result["profile"] = profile.add(result)
    return result


@app.post("/api/retrieve")
def retrieve_misconceptions(request: ExplanationRequest):
    results = retriever.retrieve(request.text, request.topic, request.limit)
    return {"query": request.text, "topic": request.topic, "count": len(results), "results": results}


@app.get("/api/profile/{session_id}")
def get_profile(session_id: str):
    return PROFILES.setdefault(session_id, Profile()).snapshot()


@app.get("/api/library")
def library():
    return {"count": len(retriever.entries), "entries": retriever.entries}


@app.post("/api/rooms")
def create_room(request: RoomRequest):
    room_id = request.room_id or uuid4().hex[:8]
    ROOMS.setdefault(room_id, set())
    return {"room_id": room_id, "join_url": f"/room/{room_id}"}


@app.websocket("/ws/{room_id}")
async def room_socket(websocket: WebSocket, room_id: str):
    await websocket.accept()
    members = ROOMS.setdefault(room_id, set())
    members.add(websocket)
    await websocket.send_json({"type": "room", "room_id": room_id, "members": len(members)})
    try:
        while True:
            message = await websocket.receive_json()
            for member in list(members):
                if member is not websocket:
                    await member.send_json(message)
    except WebSocketDisconnect:
        members.discard(websocket)
        if not members:
            ROOMS.pop(room_id, None)


@app.delete("/api/profile/{session_id}")
def reset_profile(session_id: str):
    PROFILES.pop(session_id, None)
    return {"status": "reset", "session_id": session_id}


@app.get("/api/readiness")
def readiness():
    return {
        "backend": "ready",
        "knowledge_base": {"status": "ready", "entries": len(retriever.entries)},
        "retrieval": "ready",
        "claude": "configured" if os.getenv("ANTHROPIC_API_KEY") else "not_configured",
        "demo_cache": os.getenv("USE_CACHED_RESPONSES", "false").casefold() == "true",
        "speech": "browser_native",
        "ocr": "local_asset",
        "collaboration": "ready",
    }


@app.get("/health")
def health():
    return JSONResponse({"status": "ok", "service": "mindtrace", "stage": "diagnosis"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
