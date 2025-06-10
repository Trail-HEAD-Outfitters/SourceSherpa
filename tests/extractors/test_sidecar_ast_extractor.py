import os
import json
import shutil
import tempfile
from pathlib import Path
import pytest
from src.extractors.sidecar_ast_extractor import extract_one, LANG_MAP, OUT_DIR, SOURCE_IN

@pytest.fixture(scope="function")
def temp_output_dir(monkeypatch):
    # Use a temp dir for OUT_DIR
    d = Path(tempfile.mkdtemp())
    monkeypatch.setattr("src.extractors.sidecar_ast_extractor.OUT_DIR", d)
    yield d
    shutil.rmtree(d, ignore_errors=True)

@pytest.mark.parametrize("filename,lang_id", [
    ("sample.cs", "c_sharp"),
    ("sample.html", "html"),
    ("sample.css", "css"),
    ("sample.json", "json"),
    ("sample.tsx", "tsx"),
])
def test_sidecar_ast_extractor_on_sample(filename, lang_id, temp_output_dir, sample_dir, monkeypatch):
    # Place sample file in a temp input dir
    temp_in = Path(tempfile.mkdtemp())
    src = sample_dir / filename
    dst = temp_in / filename
    if src.exists() and src.stat().st_size > 0:
        shutil.copy(src, dst)
    else:
        pytest.skip(f"No sample data for {filename}")
    monkeypatch.setattr("src.extractors.sidecar_ast_extractor.SOURCE_IN", temp_in)
    extract_one(dst)
    # Check output file
    out_file = temp_output_dir / filename
    out_file = out_file.with_suffix(dst.suffix + ".json")
    assert out_file.exists(), f"Output not created for {filename}"
    with out_file.open() as f:
        feats = json.load(f)
    assert isinstance(feats, list)
    assert feats, f"No features returned for {filename}"
    # Check lang_id in output (if present)
    if any("lang" in feat for feat in feats):
        assert any(feat["lang"] == lang_id for feat in feats if "lang" in feat)
