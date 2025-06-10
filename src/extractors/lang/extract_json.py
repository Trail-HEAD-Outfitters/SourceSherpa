from pathlib import Path, PurePath
import json

def extract_json_features(filepath: Path):
    feats = []
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for k, v in data.items():
                feats.append({
                    "filepath": str(filepath),
                    "lang": "json",
                    "type": "kv",
                    "key": k,
                    "source": json.dumps({k: v}, indent=2)
                })
        else:
            feats.append({
                "filepath": str(filepath),
                "lang": "json",
                "type": str(type(data)),
                "source": json.dumps(data, indent=2)
            })
    except Exception as e:
        feats.append({
            "filepath": str(filepath),
            "lang": "json",
            "type": "error",
            "error": str(e),
            "source": ""
        })
    return feats