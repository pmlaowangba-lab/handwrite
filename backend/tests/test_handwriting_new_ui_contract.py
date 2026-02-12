from pathlib import Path


def _load_template() -> str:
    template_path = Path(__file__).resolve().parents[2] / "templates" / "handwriting-new.html"
    return template_path.read_text(encoding="utf-8")


def test_content_editor_is_before_visual_params() -> None:
    html = _load_template()
    assert html.index("内容编辑") < html.index("视觉参数")


def test_font_selector_removed_from_visible_ui() -> None:
    html = _load_template()
    assert 'class="font-presets"' not in html
    assert '<div class="form-group" style="display:none;">' in html
    assert 'id="font-select"' in html


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


def test_preview_scale_uses_paper_size_fit_logic() -> None:
    html = _load_template()
    assert "function getPreviewScale(paper)" in html
    assert "const scale = getPreviewScale(paper);" in html
    assert "canvasContainer?.clientWidth" in html
    assert "canvasContainer?.clientHeight" in html
