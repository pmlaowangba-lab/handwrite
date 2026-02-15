from fastapi.testclient import TestClient

from app.main import app
from app.services.ai_service import PolishResult


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


def test_polish_note_endpoint(monkeypatch) -> None:
    def fake_polish_note_text(payload):  # noqa: ANN001
        return PolishResult(
            polished_text="# 产品增长复盘\n## 核心指标\n### 转化效率\n定义与计算方式说明",
            model="mock-openai",
            estimated_fill_ratio=0.82,
            target_fill_min=payload.target_fill_min,
            target_fill_max=payload.target_fill_max,
            expanded_rounds=1,
            character_count=38,
        )

    monkeypatch.setattr("app.api.v1.endpoints.ai.polish_note_text", fake_polish_note_text)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/ai/polish-note",
            json={
                "text": "请整理产品增长方法论",
                "paper_type": "a4-portrait",
                "font_size": 24,
                "line_height": 1.8,
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["polished_text"].startswith("# ")
        assert body["metadata"]["estimated_fill_ratio"] == 0.82
