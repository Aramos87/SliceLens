# POSTMORTEM

This file is also the reviewer manual. Budget about five minutes.

## What we shipped

A public URL that performs one trick well: it takes a shippable-looking accuracy, names the slice that was carrying the errors, and rewrites the headline. The idea is human-owned. The implementation is AI-assisted. The predicates are boring on purpose.

## The five-minute path

1. Open the live URL from the README.
2. Press the black button on **Negation trap**. Do not hunt for a second control.
3. Confirm the green screenshot (87.8%) gives way to a rust rewrite, and that the comparison row reads screenshot / this slice / you’d have reported (87.8% / 14% / 96.0%).
4. Click **Where did the errors go?**
5. Scroll to the FAQ. Expand **What should I click first?**
6. Optionally switch to **The average lied** and look at both badges.

If that path fails, the submission fails. Styling nits after that are secondary.

## What went right

- Bundled JSON instead of uploads. Reviewers are not a data pipeline.
- Confirm split as a first-class badge, not a footnote. The average lied exists so “did not replicate” is visible.
- Residual as exclusion of `member_id`s, not a second clustering pass.
- Tests inside the image build, so Railway cannot host a red build.

## What we cut

- Hypothesis UI. A text box that invents predicates would have been a different product and would have needed an LLM.
- Embedding clusters. Compact, uninterpretable, and off-theme.
- Extra eval themes. Theme 4 only.

## What would bite us in production

Four predicates are not a slice language. A real eval platform needs a way to add predicates without adding an LLM, plus leakage checks between discover and confirm when the split is not pre-tagged. This prototype does not pretend to be that platform.

## Ownership

The product bet — interpretable predicates plus a confirm split, not k-means — is the submission. If a reviewer disagrees with the bet, they should still be able to use the URL in one click and see that 87.8% was a lie.
