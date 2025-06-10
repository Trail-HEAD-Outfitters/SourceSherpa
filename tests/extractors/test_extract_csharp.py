from src.extractors.lang.extract_csharp import extract_csharp_features

def test_csharp_class_extraction(sample_dir):
    feats = extract_csharp_features(sample_dir / "sample.cs")
    assert feats, "No features returned"
    first = feats[0]
    assert first["type"] == "class"
    assert first["name"] == "WeatherService"
    assert "public_methods" in first