#!/usr/bin/env python3
"""Capture commercial stills and live Slice Lens frames for the narrated video."""

from __future__ import annotations

import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path("/workspace/docs")
FRAMES = ROOT / "frames"
FRAMES.mkdir(exist_ok=True)
LIVE = "https://slice-lens-production.up.railway.app"
LOCAL = "http://127.0.0.1:8765/commercial.html"
EXPLAIN = "http://127.0.0.1:8765/explainer.html"


def shot(page, name: str) -> None:
    path = FRAMES / f"{name}.png"
    page.screenshot(path=str(path), type="png")
    print("saved", path, path.stat().st_size)


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)

        for scene in range(7):
            page.goto(f"{LOCAL}?scene={scene}", wait_until="networkidle")
            page.wait_for_timeout(900)
            shot(page, f"c{scene}")

        page.goto(EXPLAIN, wait_until="networkidle")
        page.wait_for_timeout(800)
        shot(page, "explainer_top")
        page.evaluate("window.scrollTo(0, 720)")
        page.wait_for_timeout(400)
        shot(page, "explainer_mid")
        page.evaluate("document.querySelector('.arch')?.scrollIntoView({block:'center'})")
        page.wait_for_timeout(400)
        shot(page, "explainer_arch")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(400)
        shot(page, "explainer_end")

        def hold_search(route):
            time.sleep(2.4)
            route.continue_()

        page.route("**/api/runs/*/search", hold_search)
        page.goto(LIVE, wait_until="networkidle")
        page.wait_for_timeout(1000)
        shot(page, "live_idle")
        page.get_by_role("button", name="Look through this run").click()
        page.wait_for_timeout(900)
        shot(page, "live_screenshot")
        page.wait_for_selector("text=Where did the errors go", timeout=20000)
        page.wait_for_timeout(600)
        shot(page, "live_rewrite")
        page.evaluate("document.querySelector('.comparison')?.scrollIntoView({block:'center'})")
        page.wait_for_timeout(400)
        shot(page, "live_compare")
        page.evaluate("document.querySelector('.slice-list')?.scrollIntoView({block:'center'})")
        page.wait_for_timeout(400)
        shot(page, "live_slices")
        page.get_by_role("button", name="Search the residual").click()
        page.wait_for_selector("text=Nothing else is hiding", timeout=15000)
        page.wait_for_timeout(400)
        shot(page, "live_residual")

        browser.close()


if __name__ == "__main__":
    main()
