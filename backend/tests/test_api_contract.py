from fastapi.testclient import TestClient

from app.main import app


def test_health_check() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_submit_render_task() -> None:
    with TestClient(app) as client:
        payload = {
            "text": "后端化测试文本",
            "font_family": "清松手写体5-行楷",
            "paper_type": "a4-portrait",
            "paper_background": "white",
        }
        response = client.post("/api/v1/render/tasks", json=payload)
        assert response.status_code == 202
        body = response.json()
        assert body["status"] in {"pending", "running", "success"}
        assert isinstance(body["task_id"], str)
