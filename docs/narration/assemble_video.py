#!/usr/bin/env python3
"""Assemble narrated commercial and document-explainer videos."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path("/workspace/docs")
FRAMES = ROOT / "frames"
CLIPS = ROOT / "narration" / "clips"
OUT = Path("/tmp/slice-lens-video")
OUT.mkdir(exist_ok=True)


def duration(path: Path) -> float:
    raw = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(raw)


def still(img: Path, seconds: float, dest: Path, audio: Path | None = None) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-loop",
        "1",
        "-framerate",
        "30",
        "-t",
        f"{seconds:.3f}",
        "-i",
        str(img),
    ]
    if audio:
        cmd += ["-i", str(audio)]
    cmd += [
        "-vf",
        "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-tune",
        "stillimage",
    ]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
    else:
        cmd += ["-an"]
    cmd.append(str(dest))
    subprocess.check_call(cmd)


def concat(parts: list[Path], dest: Path, with_audio: bool = True) -> None:
    lst = OUT / "concat.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    cmd = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(lst),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
    ]
    if with_audio:
        cmd += ["-c:a", "aac", "-b:a", "192k"]
    else:
        cmd += ["-an"]
    cmd.append(str(dest))
    subprocess.check_call(cmd)


def mux(video: Path, audio: Path, dest: Path) -> None:
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-i",
            str(audio),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(dest),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def build_commercial() -> Path:
    mapping = [
        ("c0.png", "00_title.mp3"),
        ("c1.png", "01_win.mp3"),
        ("c2.png", "02_lie.mp3"),
        ("c3.png", "03_rewrite.mp3"),
        ("c4.png", "04_architecture.mp3"),
        ("c5.png", "05_bet.mp3"),
    ]
    parts: list[Path] = []
    for i, (img, mp3) in enumerate(mapping):
        audio = CLIPS / mp3
        dest = OUT / f"cseg_{i}.mp4"
        still(FRAMES / img, duration(audio), dest, audio)
        parts.append(dest)

    demo_audio = CLIPS / "06_demo.mp3"
    demo_dur = duration(demo_audio)
    demo_stills = [
        (FRAMES / "live_idle.png", 0.22),
        (FRAMES / "live_rewrite.png", 0.30),
        (FRAMES / "live_compare.png", 0.26),
        (FRAMES / "live_residual.png", 0.22),
    ]
    demo_parts = []
    for i, (img, share) in enumerate(demo_stills):
        dest = OUT / f"demo_{i}.mp4"
        still(img, demo_dur * share, dest)
        demo_parts.append(dest)
    demo_silent = OUT / "demo_silent.mp4"
    concat(demo_parts, demo_silent, with_audio=False)
    demo = OUT / "cseg_demo.mp4"
    mux(demo_silent, demo_audio, demo)
    parts.append(demo)

    close_audio = CLIPS / "07_close.mp3"
    close = OUT / "cseg_close.mp4"
    still(FRAMES / "c6.png", duration(close_audio), close, close_audio)
    parts.append(close)

    dest = OUT / "slice_lens_tv_commercial.mp4"
    concat(parts, dest)
    return dest


def build_explainer() -> Path:
    audio = ROOT / "slice_lens_explanation.mp3"
    total = duration(audio)
    slides = [
        (FRAMES / "explainer_top.png", 0.28),
        (FRAMES / "explainer_arch.png", 0.24),
        (FRAMES / "c4.png", 0.12),
        (FRAMES / "live_idle.png", 0.10),
        (FRAMES / "live_rewrite.png", 0.12),
        (FRAMES / "live_compare.png", 0.08),
        (FRAMES / "explainer_end.png", 0.06),
    ]
    parts = []
    for i, (img, share) in enumerate(slides):
        dest = OUT / f"exp_{i}.mp4"
        still(img, total * share, dest)
        parts.append(dest)
    silent = OUT / "explainer_silent.mp4"
    concat(parts, silent, with_audio=False)
    dest = OUT / "slice_lens_document_explained.mp4"
    mux(silent, audio, dest)
    return dest


if __name__ == "__main__":
    commercial = build_commercial()
    explainer = build_explainer()
    print("commercial", commercial, duration(commercial), commercial.stat().st_size)
    print("explainer", explainer, duration(explainer), explainer.stat().st_size)
