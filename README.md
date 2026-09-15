# Slice Lens

Headline eval accuracy hides systematic failures. Slice Lens is one interaction: a vanity number, an interpretable slice, a rewrite of what you’d have reported, then a held-out confirm.

## Use it

https://slice-lens-production.up.railway.app

The public GitHub repo is this one. No API key. No file upload. Three bundled runs. You can edit the JSON in the page; it is not saved.

## What to click

1. Stay on the **Negation trap** tab.
2. Read the left column (what the test is, the field names, three sample rows).
3. Press **Find the hidden failure**.
4. On the right, 87.8% becomes a 14% negation slice and a 96.0% “you’d have reported.”
5. Skim the FAQ at the bottom, starting with **What should I click first?**

## Demos

- **Negation trap** — `has_negation`. Screenshot 87.8% → slice 14% → you’d have reported 96.0%.
- **Units dropped** — `has_unit`. Screenshot 84.3% → slice 8%.
- **The average lied** — `has_number` confirmed; `has_uncommon_noun` did not replicate. Screenshot 77.2%.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && npm test && npm run build && cd ..
pytest
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000. `GET /health` returns `{"status":"ok"}`.

## Deploy

One Docker image. Tests run during the image build, so a red suite cannot become a live Railway service.

See [`PROBLEM_AND_SOLUTION.md`](PROBLEM_AND_SOLUTION.md) for a plain-language walkthrough of the problem, the architecture, and how the demo solves it. Open [`docs/explainer.html`](docs/explainer.html) and press **Play voice** to hear that explanation spoken (sound on). [`docs/commercial.html`](docs/commercial.html) is the TV-ad storyboard.

See also `TESTING.md`, `DESIGN.md`, and `POSTMORTEM.md`.
