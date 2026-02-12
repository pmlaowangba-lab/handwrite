from datetime import datetime

from pydantic import BaseModel, Field


class TemplateCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    config_json: dict = Field(default_factory=dict)
    created_by: str | None = None
    note: str | None = None


class TemplateResponse(BaseModel):
    id: str
    name: str
    config_json: dict
    created_by: str | None
    note: str | None
    created_at: datetime
