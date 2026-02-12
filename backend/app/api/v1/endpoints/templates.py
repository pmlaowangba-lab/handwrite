from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.templates import TemplateCreateRequest, TemplateResponse
from app.services.template_service import create_template, list_templates

router = APIRouter()


@router.get("", response_model=list[TemplateResponse])
def get_templates(db: Session = Depends(get_db)) -> list[TemplateResponse]:
    templates = list_templates(db)
    return [
        TemplateResponse(
            id=item.id,
            name=item.name,
            config_json=item.config_json,
            created_by=item.created_by,
            note=item.note,
            created_at=item.created_at,
        )
        for item in templates
    ]


@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template_item(payload: TemplateCreateRequest, db: Session = Depends(get_db)) -> TemplateResponse:
    item = create_template(db, payload)
    return TemplateResponse(
        id=item.id,
        name=item.name,
        config_json=item.config_json,
        created_by=item.created_by,
        note=item.note,
        created_at=item.created_at,
    )
