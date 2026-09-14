from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _search():
    return client.post("/api/runs/the-average-lied/search").json()


def test_has_number_confirmed():
    slices = {s["predicate"]: s for s in _search()["slices"]}
    assert "has_number" in slices
    assert slices["has_number"]["status"] == "confirmed"


def test_has_uncommon_noun_did_not_replicate():
    slices = {s["predicate"]: s for s in _search()["slices"]}
    assert "has_uncommon_noun" in slices
    assert slices["has_uncommon_noun"]["status"] == "did not replicate"


def test_average_residual_empty():
    search = _search()
    member_ids = [mid for s in search["slices"] for mid in s["member_ids"]]
    residual = client.post(
        "/api/runs/the-average-lied/residual",
        json={"member_ids": member_ids},
    ).json()
    assert residual["empty"] is True
    assert residual["message"] == "Nothing else is hiding"
