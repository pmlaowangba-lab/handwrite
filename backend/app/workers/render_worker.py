from app.services.render_service import run_render_task


def dispatch_render_task(task_id: str) -> None:
    """
    Phase 1: 使用 FastAPI BackgroundTasks 同进程执行。
    Phase 2: 迁移到 Redis + 独立 Worker。
    """
    run_render_task(task_id)
