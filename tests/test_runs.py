from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ORDER = ["negation-trap", "units-dropped", "the-average-lied"]


def test_lists_three_bundled_runs():
    response = client.get("/api/runs")
    assert response.status_code == 200
    ids = [run["id"] for run in response.json()["runs"]]
    assert ids == ORDER


def test_negation_screenshot_is_87_8():
    run = client.get("/api/runs/negation-trap").json()
    assert run["screenshot_accuracy"] == 0.878
    assert run["n"] == 500


def test_units_screenshot_is_84_3():
    run = client.get("/api/runs/units-dropped").json()
    assert run["screenshot_accuracy"] == 0.843
    assert run["n"] == 1000


def test_average_lied_screenshot_is_77_2():
    run = client.get("/api/runs/the-average-lied").json()
    assert run["screenshot_accuracy"] == 0.772
    assert run["n"] == 500
