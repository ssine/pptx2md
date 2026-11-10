"""Out-of-range --page must fail loudly instead of writing empty output."""
from pathlib import Path

import pytest
from pptx import Presentation
from pptx.util import Inches

from pptx2md.entry import convert
from pptx2md.types import ConversionConfig


def _deck(path: Path, slides: int = 1) -> Path:
    prs = Presentation()
    for i in range(slides):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        box = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(4), Inches(1))
        box.text_frame.text = f"Hello test slide number {i + 1}"
    prs.save(path)
    return path


def _config(pptx: Path, out: Path, page=None) -> ConversionConfig:
    return ConversionConfig(
        pptx_path=pptx,
        output_path=out,
        image_dir=out.parent / "img",
        page=page,
    )


def test_page_out_of_range_exits_2(tmp_path):
    pptx = _deck(tmp_path / "deck.pptx")
    out = tmp_path / "out.md"
    with pytest.raises(SystemExit) as exc:
        convert(_config(pptx, out, page=99))
    assert exc.value.code == 2
    assert not out.exists()


def test_page_in_range_still_converts(tmp_path):
    pptx = _deck(tmp_path / "deck.pptx")
    out = tmp_path / "out.md"
    convert(_config(pptx, out, page=1))
    assert "Hello test slide number 1" in out.read_text(encoding="utf-8")
