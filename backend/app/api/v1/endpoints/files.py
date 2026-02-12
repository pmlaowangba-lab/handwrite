from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.render_service import get_render_task_or_none

router = APIRouter()


@router.get("/{task_id}")
def download_render_file(task_id: str, db: Session = Depends(get_db)) -> FileResponse:
    task = get_render_task_or_none(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Render task not found")
    if task.status != "success" or not task.output_file_path:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Task not completed. current_status={task.status}",
        )

    file_path = Path(task.output_file_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Output file missing")

    filename = task.output_file_name or f"{task.id}.png"
    return FileResponse(path=file_path, media_type="image/png", filename=filename)
