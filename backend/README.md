# Backend Phase 1

本目录是手写体项目的后端骨架（Phase 1），目标是把“渲染能力”从前端迁移到后端 API。

## 已交付能力

- FastAPI 应用与 `v1` 路由
- 数据模型（用户、任务、资源、模板）
- 渲染任务 API（提交任务、查询状态、下载文件）
- AI 润色 API（OpenAI 兼容接口）
- 字体/纸张资源 API
- 基础服务健康检查 API
- PostgreSQL DDL 草案与 OpenAPI 草案

## 快速启动

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

可选：配置 AI 润色能力（使用 OpenAI 兼容网关）：

```bash
cp .env.example .env
# 按需修改 .env 中的 URL / Key / Model
# 示例：
# HW_BACKEND_AI_BASE_URL=https://gmn.chuangzuoli.com
# HW_BACKEND_AI_MODEL=gpt-5.3-codex
```

访问：

- Swagger: `http://127.0.0.1:9000/docs`
- Health: `http://127.0.0.1:9000/api/v1/health`

## 关键说明

- 默认数据库：`backend/app.db`（SQLite）
- 默认渲染输出：`backend/storage/renders`
- 资源目录默认读取项目根目录下：
  - `assets/fonts`
  - `assets/papers/processed`
- AI 润色默认读取环境变量：
  - `HW_BACKEND_AI_BASE_URL`
  - `HW_BACKEND_AI_API_KEY`
  - `HW_BACKEND_AI_MODEL`

后续 Phase 2 可切换为 `PostgreSQL + Redis + Worker`。
