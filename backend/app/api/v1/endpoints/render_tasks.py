from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.render_task import RenderTask
from app.schemas.render import RenderTaskCreateRequest, RenderTaskResponse, RenderTaskSubmitResponse
from app.services.render_service import create_render_task, get_render_task_or_none
from app.workers.render_worker import dispatch_render_task

router = APIRouter()


def _to_render_task_response(task: RenderTask) -> RenderTaskResponse:
    file_url = None
    if task.status == "success":
        file_url = f"/api/v1/files/{task.id}"

    return RenderTaskResponse(
        task_id=task.id,
        status=task.status,
        input_json=task.input_json,
        file_url=file_url,
        error_message=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
    )


@router.post("/tasks", response_model=RenderTaskSubmitResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_render_task(
    payload: RenderTaskCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> RenderTaskSubmitResponse:
    task = create_render_task(db, payload)
    background_tasks.add_task(dispatch_render_task, task.id)
    return RenderTaskSubmitResponse(task_id=task.id, status=task.status)


@router.get("/tasks/{task_id}", response_model=RenderTaskResponse)
def get_render_task(task_id: str, db: Session = Depends(get_db)) -> RenderTaskResponse:
    task = get_render_task_or_none(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Render task not found")
    return _to_render_task_response(task)
