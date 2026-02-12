from pathlib import Path


def _load_template() -> str:
    template_path = Path(__file__).resolve().parents[2] / "templates" / "handwriting-new.html"
    return template_path.read_text(encoding="utf-8")


def test_content_editor_is_before_visual_params() -> None:
    html = _load_template()
    assert html.index("内容编辑") < html.index("视觉参数")


def test_font_selector_visible_and_complete() -> None:
    html = _load_template()
    assert 'class="font-presets"' not in html
    assert '<div class="form-group" style="display:none;">' not in html
    assert 'id="font-select"' in html
    assert '<option value="清松手写体1-圆润">' in html
    assert '<option value="清松手写体8-随性">' in html
    assert '<option value="沐瑶软笔手写体">' in html
    assert '<option value="内海字体">' in html
    assert '<option value="她屿山海">' in html
    assert '<option value="栗壳坚坚体">' in html


def test_print_uses_in_page_modal_instead_of_new_window() -> None:
    html = _load_template()
    assert 'id="print-modal"' in html
    assert 'id="print-modal-confirm"' in html
    assert "window.open(" not in html
    assert "printModal.classList.add('active')" in html


def test_export_uses_canvas_image_data() -> None:
    html = _load_template()
    assert "canvas.toDataURL('image/png')" in html
    assert "link.download = `handwriting-${Date.now()}.png`" in html


def test_preview_scale_uses_fixed_paper_dpi_ratio() -> None:
    html = _load_template()
    assert "const PREVIEW_DPI = 84;" in html
    assert "const PAPER_BASE_DPI = 600;" in html
    assert "const scale = PREVIEW_DPI / PAPER_BASE_DPI;" in html
    assert "const displayWidth = Math.round(paper.w * scale);" in html
    assert "const displayHeight = Math.round(paper.h * scale);" in html


def test_canvas_uses_centered_paper_stage() -> None:
    html = _load_template()
    assert ".paper-stage {" in html
    assert 'class="paper-stage"' in html


def test_has_multi_render_modes_selector() -> None:
    html = _load_template()
    assert 'id="layout-mode-select"' in html
    assert 'value="uniform"' in html
    assert 'value="structured-fill"' in html
    assert 'value="mindmap-annotated"' in html
    assert "renderStructuredFillMode(" in html
    assert "renderMindmapAnnotatedMode(" in html
    assert "layoutModeSelect.value === 'structured-fill'" in html
    assert "layoutModeSelect.value === 'mindmap-annotated'" in html
