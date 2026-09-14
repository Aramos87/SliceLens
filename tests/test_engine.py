from pathlib import Path

from fastapi.testclient import TestClient

from app.engine import search_slices, youd_have_reported
from app.main import _demos, app
from app.predicates import evaluate, has_negation, has_number, has_uncommon_noun, has_unit

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[1]


def test_search_uses_discover_split():
    demo = _demos()["negation-trap"]
    slices = search_slices(demo["items"], run_title=demo["title"])
    assert slices
    discover_n = slices[0]["discover"]["n"]
    confirm_n = slices[0]["confirm"]["n"]
    assert discover_n >= 15
    assert discover_n != confirm_n
    assert slices[0]["discover"]["n"] + slices[0]["confirm"]["n"] == slices[0]["slice_n"]


def test_confirm_split_is_held_out():
    demo = _demos()["negation-trap"]
    items = demo["items"]
    discover_ids = {x["id"] for x in items if x["split"] == "discover"}
    confirm_ids = {x["id"] for x in items if x["split"] == "confirm"}
    assert discover_ids.isdisjoint(confirm_ids)
    slice_ = search_slices(items, run_title=demo["title"])[0]
    assert slice_["confirm"]["n"] == len(
        [x for x in items if x["predicates"]["has_negation"] and x["split"] == "confirm"]
    )


def test_residual_excludes_member_ids():
    demo = _demos()["negation-trap"]
    first = search_slices(demo["items"], run_title=demo["title"])[0]
    leftover = search_slices(
        demo["items"],
        run_title=demo["title"],
        exclude_ids=set(first["member_ids"]),
    )
    for slice_ in leftover:
        assert set(slice_["member_ids"]).isdisjoint(first["member_ids"])


def test_predicates_are_interpretable_functions():
    assert has_negation("The treaty was not ratified.")
    assert not has_negation("The treaty was ratified.")
    assert has_unit("Convert 3 km to meters.")
    assert not has_unit("What is 3 plus 4?")
    assert has_number("mean of 3, 7, and 11")
    assert not has_number("Did the committee finish the review?")
    assert has_uncommon_noun("Does the axolotl appear?")
    assert not has_uncommon_noun("Does the dog appear?")


def test_search_is_deterministic():
    demo = _demos()["the-average-lied"]
    a = search_slices(demo["items"], run_title=demo["title"])
    b = search_slices(demo["items"], run_title=demo["title"])
    assert [s["predicate"] for s in a] == [s["predicate"] for s in b]
    assert [s["status"] for s in a] == [s["status"] for s in b]


def test_complement_accuracy_formula():
    demo = _demos()["negation-trap"]
    items = demo["items"]
    reported = youd_have_reported(items, "has_negation")
    complement = [x for x in items if not x["predicates"]["has_negation"]]
    expected = sum(x["correct"] for x in complement) / len(complement)
    assert reported == expected
    assert round(reported * 1000) / 1000 == 0.96


def test_no_embedding_or_llm_imports():
    banned = ("openai", "anthropic", "sentence_transformers", "sklearn.cluster", "kmeans")
    sources = list((ROOT / "app").rglob("*.py"))
    blob = "\n".join(path.read_text() for path in sources).lower()
    for token in banned:
        assert token not in blob


def test_faq_includes_what_should_i_click_first():
    payload = client.get("/api/faq").json()
    questions = [item["question"] for item in payload["items"]]
    assert questions[0] == "What should I click first?"


def test_examples_have_ids_and_splits():
    demo = _demos()["units-dropped"]
    for item in demo["items"]:
        assert item["id"]
        assert item["split"] in {"discover", "confirm"}
        assert item["predicates"] == evaluate(item["prompt"])
        assert item["correct"] == (item["gold"].strip().lower() == item["prediction"].strip().lower())
