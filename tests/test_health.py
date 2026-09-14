from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_no_upload_route():
    paths = []
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", set()) or set()
        paths.append((path, methods))
        assert "upload" not in path.lower()
        assert "embed" not in path.lower()
    assert any(path == "/health" for path, _ in paths)
    post_paths = [path for path, methods in paths if "POST" in methods]
    assert "/api/runs/{run_id}/search" in post_paths
    assert not any("file" in path.lower() for path in post_paths)
