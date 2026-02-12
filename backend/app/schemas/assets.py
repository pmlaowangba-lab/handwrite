from pydantic import BaseModel


class FontAssetItem(BaseModel):
    id: str
    display_name: str
    file_name: str
    available: bool


class PaperAssetItem(BaseModel):
    id: str
    display_name: str
    group: str
    kind: str
    available: bool


class AssetListResponse(BaseModel):
    items: list[FontAssetItem] | list[PaperAssetItem]
