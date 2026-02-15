from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.render import PaperType


class ContentTemplate(str, Enum):
    """文案结构模板枚举"""
    CONCEPT = "concept"           # 概念讲解模板
    PRACTICAL = "practical"       # 干货流程模板
    FULL_PROCESS = "full_process" # 完整流程模板
    DECISION = "decision"         # 决策分析模板


class NotePolishRequest(BaseModel):
    content_template: ContentTemplate = ContentTemplate.CONCEPT
    text: str = Field(min_length=1, max_length=12000)
    paper_type: PaperType = PaperType.A4_PORTRAIT
    font_size: int = Field(default=24, ge=12, le=80)
    line_height: float = Field(default=1.8, ge=1.0, le=4.0)
    render_scale: float = Field(default=0.5, ge=0.2, le=1.0)
    target_fill_min: float = Field(default=0.75, ge=0.4, le=0.95)
    target_fill_max: float = Field(default=0.90, ge=0.5, le=1.0)
    max_expand_rounds: int = Field(default=1, ge=0, le=2)


class NotePolishMetadata(BaseModel):
    model: str
    layout_mode: str = "a4_note"
    estimated_fill_ratio: float
    target_fill_min: float
    target_fill_max: float
    expanded_rounds: int
    character_count: int


class NotePolishResponse(BaseModel):
    success: bool = True
    polished_text: str
    metadata: NotePolishMetadata
