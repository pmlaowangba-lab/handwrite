from sqlalchemy.orm import Session

from app.models.template import Template
from app.schemas.templates import TemplateCreateRequest


def create_template(db: Session, payload: TemplateCreateRequest) -> Template:
    template = Template(
        name=payload.name,
        config_json=payload.config_json,
        created_by=payload.created_by,
        note=payload.note,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def list_templates(db: Session) -> list[Template]:
    return db.query(Template).order_by(Template.created_at.desc()).all()
