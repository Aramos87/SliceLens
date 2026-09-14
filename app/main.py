from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.engine import residual, screenshot_accuracy, search_slices

ROOT = Path(__file__).resolve().parent.parent
DEMO_DIR = Path(__file__).resolve().parent / "demos"
FAQ_PATH = ROOT / "FAQ.md"
DIST = ROOT / "frontend" / "dist"

app = FastAPI(title="Slice Lens", version="1.0.0")


class ResidualBody(BaseModel):
    member_ids: list[str] = Field(default_factory=list)


@lru_cache(maxsize=1)
def _demos() -> dict[str, dict]:
    out = {}
    for path in sorted(DEMO_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        out[data["id"]] = data
    return out


def _summarize(demo: dict) -> dict:
    items = demo["items"]
    return {
        "id": demo["id"],
        "title": demo["title"],
        "blurb": demo["blurb"],
        "n": len(items),
        "correct": sum(1 for x in items if x["correct"]),
        "screenshot_accuracy": round(screenshot_accuracy(items) * 1000) / 1000,
        "discover_n": sum(1 for x in items if x["split"] == "discover"),
        "confirm_n": sum(1 for x in items if x["split"] == "confirm"),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/runs")
def list_runs() -> dict:
    order = ["negation-trap", "units-dropped", "the-average-lied"]
    demos = _demos()
    runs = [_summarize(demos[key]) for key in order if key in demos]
    return {"runs": runs}


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> dict:
    demo = _demos().get(run_id)
    if not demo:
        raise HTTPException(status_code=404, detail="unknown run")
    return _summarize(demo)


@app.post("/api/runs/{run_id}/search")
def search(run_id: str) -> dict:
    demo = _demos().get(run_id)
    if not demo:
        raise HTTPException(status_code=404, detail="unknown run")
    slices = search_slices(demo["items"], run_title=demo["title"])
    return {"run": _summarize(demo), "slices": slices}


@app.post("/api/runs/{run_id}/residual")
def residual_search(run_id: str, body: ResidualBody) -> dict:
    demo = _demos().get(run_id)
    if not demo:
        raise HTTPException(status_code=404, detail="unknown run")
    result = residual(demo["items"], body.member_ids, run_title=demo["title"])
    result["run"] = _summarize(demo)
    return result


@app.get("/api/faq")
def faq() -> dict:
    if not FAQ_PATH.exists():
        return {"items": []}
    items: list[dict[str, str]] = []
    question = None
    body: list[str] = []
    for line in FAQ_PATH.read_text().splitlines():
        if line.startswith("## "):
            if question:
                items.append({"question": question, "answer": "\n".join(body).strip()})
            question = line[3:].strip()
            body = []
        elif question is not None:
            body.append(line)
    if question:
        items.append({"question": question, "answer": "\n".join(body).strip()})
    return {"items": items}


if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        candidate = DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(DIST / "index.html")
