from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PaperType(str, Enum):
    A4_PORTRAIT = "a4-portrait"
    A4_LANDSCAPE = "a4-landscape"
    B5_PORTRAIT = "b5-portrait"
    B5_LANDSCAPE = "b5-landscape"
    A3_PORTRAIT = "a3-portrait"
    A3_LANDSCAPE = "a3-landscape"


class PaperBackground(str, Enum):
    WHITE = "white"
    CREAM = "cream"
    LIGHTGRAY = "lightgray"
    REAL_GRID_WHITE = "real-grid-white"
    REAL_BLANK_WHITE = "real-blank-white"
    REAL_LINED_CREAM = "real-lined-cream"
    REAL_LINED_VINTAGE = "real-lined-vintage"
    REAL_BLANK_USED = "real-blank-used"


class RenderTaskCreateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=12000)
    font_family: str = "清松手写体5-行楷"
    paper_type: PaperType = PaperType.A4_PORTRAIT
    paper_background: PaperBackground = PaperBackground.WHITE

    position_jitter: int = Field(default=10, ge=0, le=100)
    font_size: int = Field(default=24, ge=12, le=80)
    line_height: float = Field(default=1.8, ge=1.0, le=4.0)
    scratch_rate: int = Field(default=3, ge=0, le=100)
    weight_variation: int = Field(default=5, ge=0, le=100)
    note_sloppiness: int = Field(default=12, ge=0, le=100)

    render_scale: float = Field(default=0.5, ge=0.2, le=1.0)
    random_seed: int | None = None
    user_id: str | None = None


class RenderTaskSubmitResponse(BaseModel):
    task_id: str
    status: str


class RenderTaskResponse(BaseModel):
    task_id: str
    status: str
    input_json: dict
    file_url: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
