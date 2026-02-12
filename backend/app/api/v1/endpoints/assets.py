from fastapi import APIRouter

from app.schemas.assets import FontAssetItem, PaperAssetItem
from app.services.asset_service import list_font_assets, list_paper_assets

router = APIRouter()


@router.get("/fonts", response_model=list[FontAssetItem])
def get_fonts() -> list[FontAssetItem]:
    return list_font_assets()


@router.get("/papers", response_model=list[PaperAssetItem])
def get_papers() -> list[PaperAssetItem]:
    return list_paper_assets()
