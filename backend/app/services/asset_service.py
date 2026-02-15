from pathlib import Path

from app.core.config import get_settings
from app.schemas.assets import FontAssetItem, PaperAssetItem

settings = get_settings()

FONT_FILE_MAP: dict[str, str] = {
    "清松手写体1-圆润": "清松手寫體1：圓潤.ttf",
    "清松手写体2-秀气": "清松手寫體2：秀氣.ttf",
    "清松手写体3-呆萌": "清松手寫體3：呆萌.ttf",
    "清松手写体4-POP": "清松手寫體4：POP.ttf",
    "清松手写体5-行楷": "清松手寫體5：行楷.ttf",
    "清松手写体6-Q萌": "清松手寫體6：Q萌.ttf",
    "清松手写体7-飘逸": "清松手寫體7：飄逸.ttf",
    "清松手写体8-随性": "清松手寫體8：隨性.ttf",
    "沐瑶软笔手写体": "沐瑶软笔手写体.ttf",
    "沐瑶随心手写体": "沐瑶随心手写体.ttf",
    "内海字体": "內海字體-Regular-Lite.ttf",
    "她屿山海": "她屿山海.ttf",
    "栗壳坚坚体": "栗壳坚坚体.ttf",
}

PAPER_BACKGROUND_CONFIG: dict[str, dict[str, str]] = {
    "white": {"label": "纯白色", "group": "纯色背景", "kind": "color"},
    "cream": {"label": "#FFF8DC 米黄色", "group": "纯色背景", "kind": "color"},
    "lightgray": {"label": "#F5F5F5 浅灰色", "group": "纯色背景", "kind": "color"},
    "real-grid-white": {
        "label": "方格纸-白色",
        "group": "真实纸张",
        "kind": "image",
        "file_name": "grid-white-clean.jpg",
    },
    "real-blank-white": {
        "label": "空白纸-白色",
        "group": "真实纸张",
        "kind": "image",
        "file_name": "blank-white.jpg",
    },
    "real-lined-cream": {
        "label": "横线纸-米黄",
        "group": "真实纸张",
        "kind": "image",
        "file_name": "lined-cream-new.jpg",
    },
    "real-lined-vintage": {
        "label": "横线纸-复古",
        "group": "真实纸张",
        "kind": "image",
        "file_name": "lined-yellow-vintage.jpg",
    },
    "real-blank-used": {
        "label": "使用痕迹纸",
        "group": "真实纸张",
        "kind": "image",
        "file_name": "blank-used-marks.jpg",
    },
}


def resolve_font_path(font_family: str) -> Path | None:
    file_name = FONT_FILE_MAP.get(font_family)
    if not file_name:
        return None
    return settings.fonts_dir / file_name


def list_font_assets() -> list[FontAssetItem]:
    items: list[FontAssetItem] = []
    for display_name, file_name in FONT_FILE_MAP.items():
        asset_path = settings.fonts_dir / file_name
        items.append(
            FontAssetItem(
                id=display_name,
                display_name=display_name,
                file_name=file_name,
                available=asset_path.exists(),
            )
        )
    return items


def list_paper_assets() -> list[PaperAssetItem]:
    items: list[PaperAssetItem] = []
    for paper_id, config in PAPER_BACKGROUND_CONFIG.items():
        available = True
        if config["kind"] == "image":
            file_name = config.get("file_name", "")
            available = (settings.papers_dir / file_name).exists()
        items.append(
            PaperAssetItem(
                id=paper_id,
                display_name=config["label"],
                group=config["group"],
                kind=config["kind"],
                available=available,
            )
        )
    return items
