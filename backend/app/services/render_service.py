from __future__ import annotations

import random
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.render_task import RenderTask
from app.schemas.render import RenderTaskCreateRequest
from app.services.asset_service import PAPER_BACKGROUND_CONFIG, resolve_font_path

settings = get_settings()

PAPER_SIZES: dict[str, tuple[int, int]] = {
    "a4-portrait": (4960, 7015),
    "a4-landscape": (7015, 4960),
    "b5-portrait": (4157, 5905),
    "b5-landscape": (5905, 4157),
    "a3-portrait": (7015, 9921),
    "a3-landscape": (9921, 7015),
}

BACKGROUND_COLORS: dict[str, tuple[int, int, int]] = {
    "white": (255, 255, 255),
    "cream": (255, 248, 220),
    "lightgray": (245, 245, 245),
}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_render_task(db: Session, payload: RenderTaskCreateRequest) -> RenderTask:
    task = RenderTask(
        id=str(uuid4()),
        user_id=payload.user_id,
        status="pending",
        input_json=payload.model_dump(mode="json"),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_render_task_or_none(db: Session, task_id: str) -> RenderTask | None:
    return db.query(RenderTask).filter(RenderTask.id == task_id).first()


def _draw_background(image: Image.Image, paper_background: str) -> None:
    draw = ImageDraw.Draw(image)
    color = BACKGROUND_COLORS.get(paper_background)
    if color:
        draw.rectangle([(0, 0), image.size], fill=color)
        return

    config = PAPER_BACKGROUND_CONFIG.get(paper_background, {})
    file_name = config.get("file_name")
    if not file_name:
        draw.rectangle([(0, 0), image.size], fill=BACKGROUND_COLORS["white"])
        return

    bg_path = settings.papers_dir / file_name
    if not bg_path.exists():
        draw.rectangle([(0, 0), image.size], fill=BACKGROUND_COLORS["white"])
        return

    with Image.open(bg_path) as bg:
        bg = bg.convert("RGB")
        target_w, target_h = image.size
        scale = min(target_w / bg.width, target_h / bg.height)
        draw_w = int(bg.width * scale)
        draw_h = int(bg.height * scale)
        resized = bg.resize((draw_w, draw_h), Image.Resampling.LANCZOS)
        offset_x = (target_w - draw_w) // 2
        offset_y = (target_h - draw_h) // 2
        image.paste(resized, (offset_x, offset_y))


def _load_font(font_family: str, font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_path = resolve_font_path(font_family)
    if font_path and font_path.exists():
        return ImageFont.truetype(str(font_path), font_size)
    return ImageFont.load_default()


def _draw_handwriting(image: Image.Image, payload: RenderTaskCreateRequest) -> None:
    draw = ImageDraw.Draw(image)
    text_color = (30, 30, 30)
    position_jitter = payload.position_jitter / 100.0
    scratch_rate = payload.scratch_rate / 100.0
    weight_variation = payload.weight_variation / 100.0
    sloppiness = payload.note_sloppiness / 100.0

    font_size = max(12, int(payload.font_size))
    font = _load_font(payload.font_family, font_size)

    width, height = image.size
    margin_x = int(width * 0.09)
    margin_top = int(height * 0.09)
    margin_bottom = int(height * 0.09)
    max_x = width - margin_x
    max_y = height - margin_bottom
    line_step = int(font_size * payload.line_height)

    random_seed = payload.random_seed if payload.random_seed is not None else random.randint(1, 10_000_000)
    rand = random.Random(random_seed)

    cursor_y = margin_top
    for raw_line in payload.text.split("\n"):
        cursor_x = margin_x
        line_text = raw_line or " "
        for char in line_text:
            bbox = draw.textbbox((0, 0), char, font=font)
            char_width = max(1, bbox[2] - bbox[0]) + 2
            char_height = max(1, bbox[3] - bbox[1])

            if cursor_x + char_width > max_x and cursor_x > margin_x:
                cursor_x = margin_x
                cursor_y += line_step

            if cursor_y + char_height > max_y:
                return

            x_jitter = (rand.random() - 0.5) * font_size * position_jitter * (0.8 + sloppiness * 0.3)
            y_jitter = (rand.random() - 0.5) * font_size * position_jitter * (0.35 + sloppiness * 0.25)
            final_x = int(cursor_x + x_jitter)
            final_y = int(cursor_y + y_jitter)

            should_thicken = rand.random() < weight_variation
            if should_thicken:
                for _ in range(1 + rand.randint(0, 2)):
                    draw.text(
                        (final_x + rand.randint(0, 1), final_y + rand.randint(0, 1)),
                        char,
                        fill=text_color,
                        font=font,
                    )

            draw.text((final_x, final_y), char, fill=text_color, font=font)

            if rand.random() < sloppiness * 0.30:
                draw.text(
                    (final_x + rand.randint(-1, 1), final_y + rand.randint(-1, 1)),
                    char,
                    fill=(30, 30, 30, 100),
                    font=font,
                )

            if rand.random() < scratch_rate:
                mid_y = final_y + int(font_size * 0.55)
                draw.line(
                    [
                        (final_x - 2, mid_y + rand.randint(-1, 1)),
                        (final_x + char_width + 2, mid_y + rand.randint(-1, 1)),
                    ],
                    fill=text_color,
                    width=max(1, int(1 + sloppiness)),
                )

            cursor_x += char_width

        cursor_y += line_step
        if cursor_y > max_y:
            return


def render_handwriting_image(payload: RenderTaskCreateRequest, output_path: Path) -> None:
    paper_width, paper_height = PAPER_SIZES.get(payload.paper_type.value, PAPER_SIZES["a4-portrait"])
    render_scale = payload.render_scale or settings.render_scale
    width = max(720, int(paper_width * render_scale))
    height = max(1024, int(paper_height * render_scale))

    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    _draw_background(image, payload.paper_background.value)
    _draw_handwriting(image, payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="PNG", optimize=True)


def run_render_task(task_id: str) -> None:
    db = SessionLocal()
    try:
        task = get_render_task_or_none(db, task_id)
        if not task:
            return

        task.status = "running"
        task.started_at = utcnow()
        task.updated_at = utcnow()
        db.commit()

        payload = RenderTaskCreateRequest.model_validate(task.input_json)
        file_name = f"{task.id}.png"
        output_path = settings.render_dir / file_name
        render_handwriting_image(payload, output_path)

        task.status = "success"
        task.output_file_name = file_name
        task.output_file_path = str(output_path)
        task.completed_at = utcnow()
        task.updated_at = utcnow()
        db.commit()
    except Exception as exc:  # noqa: BLE001
        task = get_render_task_or_none(db, task_id)
        if task:
            task.status = "failed"
            task.error_message = str(exc)
            task.completed_at = utcnow()
            task.updated_at = utcnow()
            db.commit()
    finally:
        db.close()
