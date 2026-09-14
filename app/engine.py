"""Slice search: interpretable predicates, discovery split, held-out confirm."""

from __future__ import annotations

from dataclasses import dataclass

from app.predicates import INTERPRETATIONS, LABELS

MIN_SUPPORT = 15
MIN_DROP = 0.08
MAX_SHARE = 0.55


@dataclass(frozen=True)
class SplitStats:
    n: int
    correct: int

    @property
    def accuracy(self) -> float:
        return 0.0 if self.n == 0 else self.correct / self.n


def _stats(items: list[dict]) -> SplitStats:
    return SplitStats(n=len(items), correct=sum(1 for x in items if x["correct"]))


def _pct(accuracy: float) -> float:
    """One-decimal percent as a fraction rounded to 3 places (87.8% → 0.878)."""
    return round(accuracy * 1000) / 1000


def screenshot_accuracy(items: list[dict]) -> float:
    return _stats(items).accuracy


def youd_have_reported(items: list[dict], predicate: str) -> float:
    complement = [x for x in items if not x["predicates"].get(predicate)]
    return _stats(complement).accuracy


def _rewrite(run_title: str, slice_row: dict) -> str:
    shot = f"{slice_row['screenshot_accuracy'] * 100:.1f}%"
    slice_acc = f"{slice_row['slice_accuracy'] * 100:.1f}%"
    reported = f"{slice_row['youd_have_reported'] * 100:.1f}%"
    label = slice_row["label"]
    if slice_row["status"] == "confirmed":
        return (
            f"{run_title} screenshots at {shot}. "
            f"On “{label}” the run is {slice_acc}. "
            f"You’d have reported {reported}."
        )
    return (
        f"Discovery flagged “{label}” at {slice_acc}. "
        f"The held-out split did not replicate. Do not rewrite the {shot} headline for this one."
    )


def search_slices(
    items: list[dict],
    *,
    run_title: str = "",
    exclude_ids: set[str] | None = None,
    min_support: int = MIN_SUPPORT,
    min_drop: float = MIN_DROP,
) -> list[dict]:
    exclude_ids = exclude_ids or set()
    pool = [x for x in items if x["id"] not in exclude_ids]
    discover = [x for x in pool if x["split"] == "discover"]
    confirm = [x for x in pool if x["split"] == "confirm"]
    if not discover:
        return []

    overall_discover = _stats(discover)
    overall_confirm = _stats(confirm)
    shot = screenshot_accuracy(items)
    pred_names = sorted({name for x in pool for name in x["predicates"]})

    found: list[dict] = []
    for name in pred_names:
        d_members = [x for x in discover if x["predicates"].get(name)]
        if len(d_members) < min_support:
            continue
        share = len(d_members) / len(discover)
        if share > MAX_SHARE:
            continue
        d_stats = _stats(d_members)
        drop = overall_discover.accuracy - d_stats.accuracy
        if drop < min_drop:
            continue

        c_members = [x for x in confirm if x["predicates"].get(name)]
        c_stats = _stats(c_members)
        confirmed = (
            c_stats.n >= min_support
            and (overall_confirm.accuracy - c_stats.accuracy) >= min_drop
        )

        members = [x for x in pool if x["predicates"].get(name)]
        m_stats = _stats(members)
        failures = [x for x in members if not x["correct"]][:5]
        row = {
            "predicate": name,
            "label": LABELS.get(name, name),
            "interpretation": INTERPRETATIONS.get(name, name),
            "screenshot_accuracy": _pct(shot),
            "slice_accuracy": _pct(m_stats.accuracy),
            "slice_n": m_stats.n,
            "slice_share": _pct(m_stats.n / len(items) if items else 0.0),
            "youd_have_reported": _pct(youd_have_reported(items, name)),
            "discover": {
                "n": d_stats.n,
                "correct": d_stats.correct,
                "accuracy": _pct(d_stats.accuracy),
            },
            "confirm": {
                "n": c_stats.n,
                "correct": c_stats.correct,
                "accuracy": _pct(c_stats.accuracy),
            },
            "status": "confirmed" if confirmed else "did not replicate",
            "member_ids": [x["id"] for x in members],
            "examples": [
                {
                    "id": x["id"],
                    "prompt": x["prompt"],
                    "gold": x["gold"],
                    "prediction": x["prediction"],
                    "split": x["split"],
                }
                for x in failures
            ],
        }
        row["rewrite"] = _rewrite(run_title, row)
        found.append(row)

    found.sort(
        key=lambda r: (
            0 if r["status"] == "confirmed" else 1,
            r["discover"]["accuracy"],
            -r["slice_n"],
        )
    )
    return found


def residual(items: list[dict], member_ids: list[str], *, run_title: str = "") -> dict:
    exclude = set(member_ids)
    slices = search_slices(items, run_title=run_title, exclude_ids=exclude)
    if slices:
        return {
            "slices": slices,
            "empty": False,
            "message": None,
        }
    return {
        "slices": [],
        "empty": True,
        "message": "Nothing else is hiding",
    }
