import json
import tempfile
from pathlib import Path
from src.extractors.code_summary_extractor import SummaryExtractor, OUT_FILE

def test_summary_extractor_basic(tmp_path, monkeypatch):
    # Create a fake input JSON file
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    test_file = input_dir / "test.json"
    test_data = [
        "src/Controllers/HomeController.cs",
        {"filepath": "src/Controllers/SupportUserAccountController.cs"},
        {"value": "src/Controllers/BaseController.cs"},
    ]
    test_file.write_text(json.dumps(test_data), encoding="utf-8")

    # Patch INPUT_DIR and OUT_FILE to use temp paths
    monkeypatch.setattr("src.extractors.code_summary_extractor.INPUT_DIR", input_dir)
    out_file = tmp_path / "patterns_and_features.json"
    monkeypatch.setattr("src.extractors.code_summary_extractor.OUT_FILE", out_file)

    # Patch PATTERNS to a known value
    monkeypatch.setattr("src.extractors.code_summary_extractor.PATTERNS", [
        {"keyword": "Controller", "file_patterns": ["*Controller.cs"], "directories": ["Controllers/"]}
    ])

    extractor = SummaryExtractor(debug=False)
    extractor.walk()
    extractor.save()

    # Check output file
    assert out_file.exists()
    features = json.loads(out_file.read_text(encoding="utf-8"))
    assert len(features) == 3
    for f in features:
        assert f["value"].endswith("Controller.cs")
        assert f["group"] == "Controller"
