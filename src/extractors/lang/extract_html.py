from pathlib import Path
from tree_sitter import Parser
from src.extractors.utils.tree_sitter_loader import get_language
from src.extractors.utils import robust_get_text

HTML = get_language("html")

def extract_html_features(filepath: Path):
    parser = Parser(); parser.set_language(HTML)
    code   = filepath.read_bytes()
    tree   = parser.parse(code)
    feats  = []
    def txt(n): return robust_get_text(code, n, filepath)

    def walk(n):
        if n.type == "element":
            tag = None; attrs = {}
            for c in n.children:
                if c.type == "start_tag":
                    for sc in c.children:
                        if sc.type == "tag_name":
                            tag = txt(sc)
                        elif sc.type == "attribute":
                            k = v = None
                            for ac in sc.children:
                                if ac.type == "attribute_name":
                                    k = txt(ac)
                                elif ac.type == "quoted_attribute_value":
                                    v = txt(ac).strip('"')
                            if k: attrs[k] = v
            feats.append({
                "filepath": str(filepath),
                "lang": "html",
                "type": "element",
                "tag": tag,
                "attributes": attrs,
                "source": txt(n)
            })
        for c in n.children: walk(c)
    walk(tree.root_node)
    return feats