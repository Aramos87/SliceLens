# Slice Lens

Headline eval accuracy hides systematic failures. Slice Lens is one interaction: a vanity number, an interpretable slice, a rewrite of what you’d have reported, then a held-out confirm.

## Use it

https://slice-lens-production.up.railway.app

The public GitHub repo is this one. No API key. No upload. Three bundled runs.

## What to click

1. Leave **Negation trap** selected.
2. Press the black button.
3. Watch 87.8% become a 14% negation slice and a 96.0% “you’d have reported.”
4. Open **Where did the errors go?**
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

See `TESTING.md`, `DESIGN.md`, and `POSTMORTEM.md`.
