"""Session-only JSON playground. No disk write, no upload."""

from __future__ import annotations

from app.predicates import evaluate

MAX_ITEMS = 2000


class PlaygroundError(ValueError):
    pass


def normalize_items(raw_items: object) -> list[dict]:
    if not isinstance(raw_items, list) or not raw_items:
        raise PlaygroundError("items must be a non-empty list")
    if len(raw_items) > MAX_ITEMS:
        raise PlaygroundError(f"at most {MAX_ITEMS} items")

    seen: set[str] = set()
    out: list[dict] = []
    for index, raw in enumerate(raw_items):
        if not isinstance(raw, dict):
            raise PlaygroundError(f"item {index} must be an object")
        prompt = str(raw.get("prompt") or "").strip()
        if not prompt:
            raise PlaygroundError(f"item {index} needs a prompt")
        gold = str(raw.get("gold") or "").strip()
        prediction = str(raw.get("prediction") or "").strip()
        split = str(raw.get("split") or "discover").strip()
        if split not in {"discover", "confirm"}:
            raise PlaygroundError(f"item {index} split must be discover or confirm")
        item_id = str(raw.get("id") or f"edit-{index:04d}")
        if item_id in seen:
            item_id = f"{item_id}-{index}"
        seen.add(item_id)
        out.append(
            {
                "id": item_id,
                "prompt": prompt,
                "gold": gold,
                "prediction": prediction,
                "correct": gold.lower() == prediction.lower(),
                "split": split,
                "predicates": evaluate(prompt),
            }
        )
    return out


def pack_from_payload(payload: dict) -> dict:
    title = str(payload.get("title") or "Edited run").strip() or "Edited run"
    run_id = str(payload.get("id") or "edited-run")
    items = normalize_items(payload.get("items"))
    return {
        "id": run_id,
        "title": title,
        "blurb": str(payload.get("blurb") or "Session edit. Not saved."),
        "items": items,
    }
