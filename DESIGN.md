# DESIGN

Slice Lens is Theme 4 of the take-home: a self-contained eval tool whose immediate use is a URL.

## Claim

A single accuracy number is a screenshot, not a finding. Systematic failures hide under it. The useful move is not “cluster the errors.” It is: name a predicate, measure the slice, rewrite the headline you would have reported, and ask a held-out split whether the name still holds.

## One interaction

The page is two columns inside a tab per demo. Left is the test: what the questions are, what each field means, three sample rows, and the button. Right is the finding.

1. **Vanity number** — overall accuracy on the bundled run. This is the green hero, the screenshot.
2. **Interpretable slice** — a boolean predicate with an English label (`has negation`).
3. **Rewrite** — rust hero plus the comparison row: screenshot / this slice / you’d have reported.
4. **Confirm** — the same predicate on a split that was not used to decide whether the slice exists.

A collapsed JSON editor on the left can re-run the same search on an in-memory edit. Nothing is uploaded or written to disk.

## Why predicates, not k-means

Embeddings would give compact blobs and a slide titled “Cluster 3.” A reviewer cannot act on Cluster 3. A predicate is a sentence: “the prompt contains a negation.” You can write a unit test for it. You can grep a new eval for it. You can disagree with it.

The search is deliberately small. Four functions in `app/predicates.py`. No API keys. The interesting work is the confirm split and the complement rewrite, not a larger hypothesis language.

## Splits

Each item is tagged `discover` or `confirm`. Search only promotes a predicate if discovery accuracy is worse than the discovery base rate by a fixed drop, with a minimum support. **confirmed** requires the same drop on confirm. **did not replicate** keeps the discovery slice on screen so the tool can be wrong in public. The average lied demo exists for that case: `has_number` holds, `has_uncommon_noun` does not.

## Residual

Residual search excludes every `member_id` already claimed by the returned slices, then searches again. It is not a second product. It answers “is that all.” The empty state is a full sentence: **Nothing else is hiding**.

## Non-goals

- Eval upload
- LLM-proposed hypotheses
- Embedding clusters
- Extra themes
- A GitHub Pages TypeScript port

## Stack

Python 3.12, FastAPI, a Vite React UI, one Docker image. The UI is a single page because the product is a single interaction. `GET /health` is `{ "status": "ok" }` so Railway can tell the process is alive.
