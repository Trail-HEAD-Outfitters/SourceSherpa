from pathlib import Path
from tree_sitter import Parser
from src.extractors.utils.tree_sitter_loader import get_language
from src.extractors.utils import robust_get_text

CSS = get_language("css")

def extract_css_features(filepath: Path):
    parser = Parser(); parser.set_language(CSS)
    code   = filepath.read_bytes()
    tree   = parser.parse(code)
    feats  = []
    def txt(n): return robust_get_text(code, n, filepath)

    def walk(n):
        if n.type == "rule_set":
            selector = next((txt(c) for c in n.children if c.type == "selectors"), "")
            feats.append({
                "filepath": str(filepath),
                "lang": "css",
                "type": "rule_set",
                "selector": selector,
                "source": txt(n)
            })
        elif n.type == "media_statement":
            feats.append({
                "filepath": str(filepath),
                "lang": "css",
                "type": "media_statement",
                "source": txt(n)
            })
        for c in n.children: walk(c)
    walk(tree.root_node)
    return feats