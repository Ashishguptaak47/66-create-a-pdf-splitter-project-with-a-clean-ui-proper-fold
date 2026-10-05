import os
import pytest
from reportlab.pdfgen import canvas
from main import PDFSplitterLogic

@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    c = canvas.Canvas(str(pdf_path))
    for i in range(1, 6):
        c.drawString(100, 100, f"Page {i}")
        c.showPage()
    c.save()
    return str(pdf_path)

def test_parse_ranges():
    assert PDFSplitterLogic.parse_ranges("1-3, 5", 5) == [0, 1, 2, 4]
    assert PDFSplitterLogic.parse_ranges("2", 5) == [1]
    with pytest.raises(ValueError):
        PDFSplitterLogic.parse_ranges("1-6", 5)
    with pytest.raises(ValueError):
        PDFSplitterLogic.parse_ranges("invalid", 5)

def test_split_every(sample_pdf, tmp_path):
    out_dir = tmp_path / "output"
    created = PDFSplitterLogic.split_pdf(sample_pdf, str(out_dir), "every")
    assert len(created) == 5
    for f in created:
        assert os.path.exists(f)

def test_split_custom(sample_pdf, tmp_path):
    out_dir = tmp_path / "output"
    created = PDFSplitterLogic.split_pdf(sample_pdf, str(out_dir), "custom", range_str="1, 3-4")
    assert len(created) == 1
    assert os.path.exists(created[0])

def test_missing_file():
    with pytest.raises(FileNotFoundError):
        PDFSplitterLogic.split_pdf("non_existent.pdf", "out", "every")
