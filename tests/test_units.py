from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_units_slice_is_has_unit():
    payload = client.post("/api/runs/units-dropped/search").json()
    assert payload["slices"][0]["predicate"] == "has_unit"
    assert payload["slices"][0]["label"] == "has unit"


def test_units_slice_accuracy_is_8():
    slice_ = client.post("/api/runs/units-dropped/search").json()["slices"][0]
    assert slice_["slice_accuracy"] == 0.08


def test_units_confirmed():
    slice_ = client.post("/api/runs/units-dropped/search").json()["slices"][0]
    assert slice_["status"] == "confirmed"
    assert slice_["confirm"]["accuracy"] <= 0.2
