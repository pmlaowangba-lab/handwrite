from fastapi import APIRouter, HTTPException, status

from app.schemas.ai import NotePolishMetadata, NotePolishRequest, NotePolishResponse
from app.services.ai_service import AiConfigurationError, AiServiceError, polish_note_text

router = APIRouter()


@router.post("/polish-note", response_model=NotePolishResponse)
def polish_note(payload: NotePolishRequest) -> NotePolishResponse:
    try:
        result = polish_note_text(payload)
    except AiConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except AiServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return NotePolishResponse(
        polished_text=result.polished_text,
        metadata=NotePolishMetadata(
            model=result.model,
            layout_mode=result.layout_mode,
            estimated_fill_ratio=result.estimated_fill_ratio,
            target_fill_min=result.target_fill_min,
            target_fill_max=result.target_fill_max,
            expanded_rounds=result.expanded_rounds,
            character_count=result.character_count,
        ),
    )
