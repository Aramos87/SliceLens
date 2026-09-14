"""Plain-language copy and sample rows for the left column."""

from __future__ import annotations

from app.predicates import INTERPRETATIONS, LABELS

DEMO_GUIDE: dict[str, dict] = {
    "negation-trap": {
        "one_line": "Yes/no questions. Some contain “not”, “never”, or “no”.",
        "success": "The model should answer no when the fact is negated.",
        "expect": "A high overall score can hide a group of negated questions the model almost always misses.",
        "focus": "has_negation",
        "predicates": ["has_negation"],
    },
    "units-dropped": {
        "one_line": "Convert a number that already has a unit (km → meters).",
        "success": "The model should convert the number, not copy it.",
        "expect": "Most arithmetic looks fine. The failures pile up when a unit is present.",
        "focus": "has_unit",
        "predicates": ["has_unit"],
    },
    "the-average-lied": {
        "one_line": "A mix of averages and rare-word questions.",
        "success": "A real weak group should fail on both halves of the data.",
        "expect": "One pattern will hold on the held-out half. Another will look real and then vanish.",
        "focus": "has_number",
        "predicates": ["has_number", "has_uncommon_noun"],
    },
}

FIELD_GLOSSARY = [
    {"key": "prompt", "label": "prompt", "meaning": "The question the model was asked."},
    {"key": "gold", "label": "gold", "meaning": "The correct answer."},
    {"key": "prediction", "label": "prediction", "meaning": "What the model said."},
    {"key": "correct", "label": "correct", "meaning": "Yes if gold and prediction match."},
    {
        "key": "split",
        "label": "split",
        "meaning": "discover is used to find a pattern. confirm is held out to check it.",
    },
]


def _card(item: dict, why: str, kind: str) -> dict:
    return {
        "id": item["id"],
        "kind": kind,
        "prompt": item["prompt"],
        "gold": item["gold"],
        "prediction": item["prediction"],
        "correct": item["correct"],
        "split": item["split"],
        "why": why,
    }


def sample_examples(demo: dict) -> list[dict]:
    guide = DEMO_GUIDE.get(demo["id"], {})
    focus = guide.get("focus")
    items = demo["items"]
    cards: list[dict] = []

    easy = next(
        (
            x
            for x in items
            if x["correct"] and (not focus or not x["predicates"].get(focus))
        ),
        None,
    )
    if easy:
        cards.append(
            _card(
                easy,
                "No trick in the question. Rows like this make the overall score look fine.",
                "easy pass",
            )
        )

    fail = next(
        (
            x
            for x in items
            if not x["correct"] and (not focus or x["predicates"].get(focus))
        ),
        None,
    )
    if fail:
        cards.append(
            _card(
                fail,
                "This is the kind of miss the overall score is hiding.",
                "typical miss",
            )
        )

    extra = next(
        (
            x
            for x in items
            if x["id"] not in {c["id"] for c in cards} and x["correct"] != bool(fail)
        ),
        None,
    )
    if extra is None:
        extra = next((x for x in items if x["id"] not in {c["id"] for c in cards}), None)
    if extra:
        cards.append(
            _card(
                extra,
                "Same format, different outcome. Compare this with the miss above.",
                "compare",
            )
        )
    return cards[:3]


def guide_for(demo: dict) -> dict:
    meta = DEMO_GUIDE.get(demo["id"], {})
    pred_names = meta.get("predicates") or []
    return {
        "one_line": meta.get("one_line", demo.get("blurb", "")),
        "success": meta.get("success", ""),
        "expect": meta.get("expect", ""),
        "predicates": [
            {
                "key": name,
                "label": LABELS.get(name, name),
                "meaning": INTERPRETATIONS.get(name, name),
            }
            for name in pred_names
        ],
        "fields": FIELD_GLOSSARY,
        "examples": sample_examples(demo),
    }
