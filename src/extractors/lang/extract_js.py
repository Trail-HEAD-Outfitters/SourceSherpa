from pathlib import Path
from tree_sitter import Parser
from src.extractors.utils.tree_sitter_loader import get_language
from src.extractors.utils import robust_get_text

TSX = get_language("tsx")  # covers tsx/jsx; for pure ts use "typescript"

def extract_js_features(filepath: Path):
    parser = Parser(); parser.set_language(TSX)
    code   = filepath.read_bytes()
    tree   = parser.parse(code)
    feats  = []
    def txt(n): return robust_get_text(code, n, filepath)

    def walk(n):
        if n.type == "class_declaration":
            cls = next((txt(c) for c in n.children if c.type == "identifier"), None)
            meths = [
                txt(mn) for m in n.walk().node.children
                if m.type == "method_definition"
                for mn in m.children if mn.type == "property_identifier"
            ]
            feats.append({
                "filepath": str(filepath), "lang": "typescript",
                "type": "class", "name": cls, "methods": meths,
                "source": txt(n)
            })
        elif n.type == "function_declaration":
            fn = next((txt(c) for c in n.children if c.type == "identifier"), None)
            feats.append({
                "filepath": str(filepath), "lang": "typescript",
                "type": "function", "name": fn, "source": txt(n)
            })
        for c in n.children: walk(c)
    walk(tree.root_node)
    return feats