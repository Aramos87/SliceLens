#!/usr/bin/env python3
"""Build timed commercial voiceover clips with Edge TTS."""

from __future__ import annotations

import asyncio
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent
CLIPS = ROOT / "clips"
CLIPS.mkdir(parents=True, exist_ok=True)

SCENES = [
    ("00_title", "Slice Lens."),
    (
        "01_win",
        "Eighty-seven point eight percent. That's the number you'd paste into a launch post. Looks like a win.",
    ),
    (
        "02_lie",
        "Until you look at the prompts with a negation. Fourteen percent. Same model. Same eval. The average was a blend. The average was a lie.",
    ),
    (
        "03_rewrite",
        "Introducing Slice Lens. One click names the slice that was carrying the errors. Then it rewrites the headline you already wanted to ship. You'd have reported ninety-six percent. That's the rest of the run — the part that was covering for the failure.",
    ),
    (
        "04_architecture",
        "How? One page. One engine. Four named predicates. A reviewer talks to a React app. The app talks to FastAPI. The engine searches a tiny library: negation, units, numbers, rare nouns. It hunts on a discover split. Then it asks a held-out confirm split: does this still hold?",
    ),
    (
        "05_bet",
        "No uploads. No API keys. No mysterious Cluster Three. A cluster you cannot name is not a finding. A sentence is.",
    ),
    (
        "06_demo",
        "Watch. Leave Negation trap selected. Press the black button. Green screenshot — eighty-seven point eight. Rust rewrite — fourteen percent. You'd have reported ninety-six. Confirmed on a split the search was not allowed to see.",
    ),
    (
        "07_close",
        "And if it doesn't replicate? We keep the miss on screen. Because an eval tool that can only celebrate... is a commercial. Slice Lens is the other kind. Don't ship the screenshot. Name the slice.",
    ),
]


async def synth(name: str, text: str) -> None:
    out = CLIPS / f"{name}.mp3"
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural", rate="+6%", pitch="-4Hz")
    await communicate.save(str(out))
    print(name, out.stat().st_size)


async def main() -> None:
    for name, text in SCENES:
        await synth(name, text)


if __name__ == "__main__":
    asyncio.run(main())
