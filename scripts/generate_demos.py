#!/usr/bin/env python3
"""Build the three bundled eval JSON files with locked headline numbers."""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.predicates import evaluate  # noqa: E402

OUT = ROOT / "app" / "demos"

ENTITIES = [
    "committee",
    "treaty",
    "patient",
    "sensor",
    "invoice",
    "reactor",
    "ballot",
    "sample",
    "lease",
    "probe",
    "widget",
    "ledger",
    "capsule",
    "relay",
    "permit",
]
ACTIONS = [
    "approved",
    "ratified",
    "received",
    "triggered",
    "posted",
    "sealed",
    "counted",
    "logged",
    "signed",
    "calibrated",
]
OBJECTS = [
    "the bill",
    "the accord",
    "the dose",
    "the alarm",
    "the charge",
    "the core",
    "the vote",
    "the batch",
    "the rider",
    "the gyro",
]


def _id(prefix: str, i: int) -> str:
    return f"{prefix}-{i:04d}"


def _item(prefix: str, i: int, prompt: str, gold: str, pred: str, split: str) -> dict:
    text = prompt
    correct = gold.strip().lower() == pred.strip().lower()
    return {
        "id": _id(prefix, i),
        "prompt": prompt,
        "gold": gold,
        "prediction": pred,
        "correct": correct,
        "split": split,
        "predicates": evaluate(text),
    }


def _split_for(i: int, n: int, confirm_frac: float = 0.4) -> str:
    # Deterministic: last confirm_frac of each contiguous block go to confirm.
    return "confirm" if (i / n) >= (1 - confirm_frac) else "discover"


def negation_trap() -> dict:
    """87.8% overall, has_negation at 14%, complement 96.0%."""
    items: list[dict] = []
    n_slice = 50
    slice_correct = 7  # 14%
    # 30 discover / 20 confirm. Put 4 correct in discover, 3 in confirm.
    correct_idx = set(range(4)) | set(range(30, 33))

    templates_fail = [
        "The {e} did not {a} {o}. Did the {e} {a} {o}?",
        "There was never a record that the {e} {a} {o}. Did the {e} {a} {o}?",
        "Nobody on the {e} {a} {o}. Did the {e} {a} {o}?",
        "The {e} cannot have {a} {o}. Did the {e} {a} {o}?",
        "There is no sign the {e} {a} {o}. Did the {e} {a} {o}?",
        "The {e} went without having {a} {o}. Did the {e} {a} {o}?",
    ]
    templates_pass = [
        "The {e} did not {a} {o}. Did the {e} {a} {o}?",
    ]

    for i in range(n_slice):
        e, a, o = ENTITIES[i % len(ENTITIES)], ACTIONS[i % len(ACTIONS)], OBJECTS[i % len(OBJECTS)]
        gold = "no"
        if i in correct_idx:
            prompt = templates_pass[0].format(e=e, a=a, o=o)
            pred = "no"
        else:
            prompt = templates_fail[i % len(templates_fail)].format(e=e, a=a, o=o)
            pred = "yes"
        split = "discover" if i < 30 else "confirm"
        items.append(_item("neg", i, prompt, gold, pred, split))

    # 450 complement: 432 correct (96.0%). 18 errors with no shared predicate.
    n_comp = 450
    n_comp_correct = 432
    facts = [
        ("The {e} {a} {o} on Tuesday. Did the {e} {a} {o}?", "yes"),
        ("The {e} {a} {o} after review. Did the {e} {a} {o}?", "yes"),
        ("Minutes show the {e} {a} {o}. Did the {e} {a} {o}?", "yes"),
        ("A clerk saw that the {e} {a} {o}. Did the {e} {a} {o}?", "yes"),
    ]
    for j in range(n_comp):
        e = ENTITIES[j % len(ENTITIES)]
        a = ACTIONS[(j + 3) % len(ACTIONS)]
        o = OBJECTS[(j + 1) % len(OBJECTS)]
        tmpl, gold = facts[j % len(facts)]
        prompt = tmpl.format(e=e, a=a, o=o)
        correct = j < n_comp_correct
        pred = gold if correct else ("no" if gold == "yes" else "yes")
        split = "discover" if j < 270 else "confirm"
        items.append(_item("neg", n_slice + j, prompt, gold, pred, split))

    return _pack(
        "negation-trap",
        "Negation trap",
        "Yes/no reading of a short fact. The model drops the negation and answers the affirmative.",
        items,
    )


def units_dropped() -> dict:
    """84.3% overall, has_unit at 8%."""
    items: list[dict] = []
    n_slice = 50
    # 4 correct of 50 = 8%. 2 in discover (of 30), 2 in confirm (of 20).
    correct_idx = {0, 1, 30, 31}

    conversions = [
        ("A rod is 2.5 km long. How many meters is that?", "2500", "2.5"),
        ("A bag weighs 3 kg. What is that in grams?", "3000", "3"),
        ("The sample is 12 cm wide. How many millimeters is that?", "120", "12"),
        ("The flask holds 2 l. How many milliliters is that?", "2000", "2"),
        ("It is 10 celsius. What is that in celsius still, as a number?", "10", "50"),
        ("A parcel is 4 lb. Report the listed pounds.", "4", "64"),
        ("The gap is 8 mm. How many mm is the gap?", "8", "0.8"),
        ("Tank volume is 500 ml. How many ml is that?", "500", "0.5"),
        ("Walk 1.2 km. How many meters?", "1200", "1.2"),
        ("Mass 0.5 kg. How many grams?", "500", "0.5"),
    ]

    for i in range(n_slice):
        prompt, gold, wrong = conversions[i % len(conversions)]
        # Vary the number slightly so rows aren't identical, while keeping a unit.
        if i >= len(conversions):
            n = 1 + (i % 9)
            prompt = f"Convert {n} km to meters."
            gold = str(n * 1000)
            wrong = str(n)
        pred = gold if i in correct_idx else wrong
        split = "discover" if i < 30 else "confirm"
        items.append(_item("unit", i, prompt, gold, pred, split))

    # 950 complement, 839 correct → overall 843/1000 = 84.3%
    n_comp = 950
    n_comp_correct = 839
    for j in range(n_comp):
        a, b = 2 + (j % 17), 3 + (j % 11)
        prompt = f"What is {a} plus {b}?"
        gold = str(a + b)
        correct = j < n_comp_correct
        pred = gold if correct else str(a + b + 1)
        split = "discover" if j < 570 else "confirm"
        items.append(_item("unit", n_slice + j, prompt, gold, pred, split))

    return _pack(
        "units-dropped",
        "Units dropped",
        "Unit conversion. The model copies the number and drops the conversion.",
        items,
    )


def average_lied() -> dict:
    """77.2% overall. has_number confirmed; has_uncommon_noun did not replicate."""
    items: list[dict] = []
    idx = 0

    # 120 has_number, 48 correct (40%).
    # discover 72 with 28 correct; confirm 48 with 20 correct.
    n_num = 120
    num_correct_discover = set(range(28))
    num_correct_confirm = set(range(72, 92))
    for i in range(n_num):
        xs = [i % 9 + 1, (i * 3) % 9 + 2, (i * 5) % 9 + 1]
        prompt = f"What is the mean of {xs[0]}, {xs[1]}, and {xs[2]}?"
        mean = round(sum(xs) / 3, 1)
        gold = str(mean)
        split = "discover" if i < 72 else "confirm"
        is_correct = i in num_correct_discover or i in num_correct_confirm
        pred = gold if is_correct else str(xs[0])  # model returns the first number
        items.append(_item("avg", idx, prompt, gold, pred, split))
        idx += 1

    nouns = [
        "axolotl",
        "quark",
        "obsidian",
        "fjord",
        "kudu",
        "narwhal",
        "ptarmigan",
        "qat",
        "xylem",
        "yttrium",
    ]
    # 40 uncommon-noun items, disjoint from numbers (no digits in the prompt).
    # discover 24 with 8 correct (33%); confirm 16 with 15 correct (93.75%).
    n_noun = 40
    noun_correct = set(range(8)) | set(range(25, 40))  # 8 discover + 15 confirm
    for i in range(n_noun):
        noun = nouns[i % len(nouns)]
        prompt = f"The cited passage is about weather. Does it mention the {noun}?"
        gold = "no"
        split = "discover" if i < 24 else "confirm"
        pred = gold if i in noun_correct else "yes"
        items.append(_item("avg", idx, prompt, gold, pred, split))
        idx += 1

    # remaining 340, 315 correct → overall 48+23+315 = 386 / 500 = 77.2%
    n_rest = 340
    n_rest_correct = 315
    for j in range(n_rest):
        prompt = f"Did the {ENTITIES[j % len(ENTITIES)]} finish the review?"
        gold = "yes"
        pred = "yes" if j < n_rest_correct else "no"
        split = "discover" if j < 204 else "confirm"
        items.append(_item("avg", idx, prompt, gold, pred, split))
        idx += 1

    return _pack(
        "the-average-lied",
        "The average lied",
        "Mixed reading and arithmetic. A number slice is real; an uncommon-noun slice is a discovery fluke.",
        items,
    )


def _pack(run_id: str, title: str, blurb: str, items: list[dict]) -> dict:
    correct = sum(1 for x in items if x["correct"])
    return {
        "id": run_id,
        "title": title,
        "blurb": blurb,
        "items": items,
        "n": len(items),
        "correct": correct,
        "screenshot_accuracy": correct / len(items),
    }


def _validate(demo: dict) -> None:
    for item in demo["items"]:
        expected = evaluate(item["prompt"])
        if item["predicates"] != expected:
            raise SystemExit(
                f"{demo['id']} {item['id']} predicate mismatch: {item['predicates']} vs {expected}\n{item['prompt']}"
            )
        gold_ok = item["correct"] == (item["gold"].strip().lower() == item["prediction"].strip().lower())
        if not gold_ok:
            raise SystemExit(f"{demo['id']} {item['id']} correct flag mismatch")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    demos = [negation_trap(), units_dropped(), average_lied()]
    for demo in demos:
        _validate(demo)
        path = OUT / f"{demo['id']}.json"
        path.write_text(json.dumps(demo, indent=2) + "\n")
        acc = demo["screenshot_accuracy"]
        print(f"wrote {path.name}: n={demo['n']} acc={acc:.3f} ({demo['correct']}/{demo['n']})")

        from collections import defaultdict

        by_pred = defaultdict(lambda: {"n": 0, "c": 0, "disc_n": 0, "disc_c": 0, "conf_n": 0, "conf_c": 0})
        for it in demo["items"]:
            for name, flag in it["predicates"].items():
                if not flag:
                    continue
                by_pred[name]["n"] += 1
                by_pred[name]["c"] += int(it["correct"])
                key_n = "disc_n" if it["split"] == "discover" else "conf_n"
                key_c = "disc_c" if it["split"] == "discover" else "conf_c"
                by_pred[name][key_n] += 1
                by_pred[name][key_c] += int(it["correct"])
        for name, s in by_pred.items():
            print(
                f"  {name}: {s['c']}/{s['n']}={s['c']/s['n']:.3f} "
                f"disc {s['disc_c']}/{s['disc_n']} conf {s['conf_c']}/{s['conf_n']}"
            )


if __name__ == "__main__":
    random.seed(4)
    main()
