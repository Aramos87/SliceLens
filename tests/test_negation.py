from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _search():
    return client.post("/api/runs/negation-trap/search").json()


def test_negation_slice_accuracy_is_14():
    payload = _search()
    slice_ = payload["slices"][0]
    assert slice_["predicate"] == "has_negation"
    assert slice_["slice_accuracy"] == 0.14


def test_negation_youd_have_reported_96():
    slice_ = _search()["slices"][0]
    assert slice_["youd_have_reported"] == 0.96


def test_negation_predicate_is_has_negation():
    slice_ = _search()["slices"][0]
    assert slice_["label"] == "has negation"
    assert "negation" in slice_["interpretation"].lower()


def test_negation_confirmed_on_held_out():
    slice_ = _search()["slices"][0]
    assert slice_["status"] == "confirmed"
    assert slice_["confirm"]["n"] >= 15
    assert slice_["confirm"]["accuracy"] < 0.5


def test_negation_residual_empty():
    search = _search()
    member_ids = [mid for s in search["slices"] for mid in s["member_ids"]]
    residual = client.post(
        "/api/runs/negation-trap/residual",
        json={"member_ids": member_ids},
    ).json()
    assert residual["empty"] is True
    assert residual["message"] == "Nothing else is hiding"
    assert residual["slices"] == []
