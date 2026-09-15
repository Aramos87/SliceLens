from fastapi.testclient import TestClient

from app.main import _demos, app
from app.playground import PlaygroundError, normalize_items

client = TestClient(app)


def test_pack_returns_bundled_items():
    pack = client.get("/api/runs/negation-trap/pack").json()
    assert pack["id"] == "negation-trap"
    assert len(pack["items"]) == 500


def test_examples_include_a_pass_and_a_miss():
    payload = client.get("/api/runs/negation-trap/examples").json()
    kinds = [card["kind"] for card in payload["guide"]["examples"]]
    assert "easy pass" in kinds
    assert "typical miss" in kinds
    assert len(payload["guide"]["examples"]) == 3
    assert payload["guide"]["fields"]
    assert payload["guide"]["predicates"][0]["key"] == "has_negation"


def test_analyze_bundled_negation_matches_search():
    pack = client.get("/api/runs/negation-trap/pack").json()
    analyzed = client.post("/api/analyze", json=pack).json()
    searched = client.post("/api/runs/negation-trap/search").json()
    assert analyzed["slices"][0]["predicate"] == "has_negation"
    assert analyzed["slices"][0]["slice_accuracy"] == searched["slices"][0]["slice_accuracy"]
    assert analyzed["slices"][0]["youd_have_reported"] == 0.96


def test_analyze_rejects_empty_items():
    response = client.post("/api/analyze", json={"title": "x", "items": []})
    assert response.status_code == 400


def test_analyze_recomputes_predicates_from_prompt():
    items = normalize_items(
        [{"prompt": "The door was not locked. Was the door locked?", "gold": "no", "prediction": "yes"}]
    )
    assert items[0]["predicates"]["has_negation"] is True
    assert items[0]["correct"] is False


def test_normalize_rejects_bad_split():
    try:
        normalize_items([{"prompt": "hi", "split": "train"}])
        raise AssertionError("expected PlaygroundError")
    except PlaygroundError as exc:
        assert "split" in str(exc)
