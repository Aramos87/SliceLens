# TESTING

Tests are the deploy gate. The Docker image runs Vitest while building the frontend and Pytest while building the API layer. If either suite is red, `docker build` fails and Railway has nothing to start.

## Suites

- **pytest**: 26 tests. Health, the three bundled numbers, slice search, confirm vs did-not-replicate, residual empty state, predicate functions, no upload/LLM surface.
- **vitest**: 7 tests. Dashed step, black button, green screenshot hero, rust rewrite, comparison row, badge legend, FAQ first question.

```bash
pip install -r requirements.txt
pytest
cd frontend && npm install && npm test
```

## Numbers the suite pins

| Run | Screenshot | Open slice | You’d have reported |
| --- | --- | --- | --- |
| Negation trap | 87.8% | `has_negation` 14% | 96.0% |
| Units dropped | 84.3% | `has_unit` 8% | complement of that slice |
| The average lied | 77.2% | `has_number` confirmed, `has_uncommon_noun` did not replicate | — |

## What is not tested here

There is no live OpenAI call to mock. There is no upload parser. If a future change adds either, it is out of scope for this product, not a missing test.
