# FAQ

## What should I click first?

Open the Negation trap tab. Read the left column — the story, the field names, and the three sample rows. Press Find the hidden failure. The right column should show 87.8% / 14% / 96.0% you’d have reported.

## Where did the errors go?

They were never evenly spread. On Negation trap they concentrate on prompts that contain a negation. The screenshot still says 87.8% because the rest of the run is 96.0%. Open the comparison row: screenshot / this slice / you’d have reported.

## What does “you’d have reported” mean?

Accuracy on the complement — every item that is not in the open slice. It is the number you would have put in a launch screenshot if this failure mode were not in the eval. It is not a promise the model is good. It is a rewrite of the headline you already wanted to ship.

## What do the badges mean?

confirmed means the same predicate is still much worse on a held-out confirm split. did not replicate means discovery looked interesting and the confirm split did not agree. Switch to The average lied to see both badges on the same run.

## Why is there a residual button?

After you take the open slices out (every member_id they own), search again. If nothing systematic remains, Slice Lens says “Nothing else is hiding.” Residual does not sit under a negative-margin hint. It is a normal control under the slices.

## Why not embeddings or k-means?

A cluster you cannot name is not an actionable eval finding. Slice Lens only searches a tiny library of interpretable predicates (`has_negation`, `has_unit`, `has_number`, `has_uncommon_noun`). The confirm split is there because even a named predicate can overfit discovery.

## Can I upload my own eval?

No file picker, no API key. You can open Edit this run (JSON), change the bundled questions, and press Run my edit. That stays in this browser session and is not saved.

## What should a reviewer spend five minutes on?

Open Negation trap. Read the left column. Press Find the hidden failure. Read the rust rewrite. Open this FAQ. Skim DESIGN.md and POSTMORTEM.md.
