# src/extractors/lang/extract_csharp.py   (example for C#)
from tree_sitter import Parser
from src.extractors.utils.tree_sitter_loader import get_language
from src.extractors.utils import robust_get_text  # your helper

LANG_ID = "c_sharp"       # grammar name in my-languages.so or wheel
LANG    = get_language(LANG_ID)

def extract_csharp_features(filepath):
    parser = Parser(); parser.set_language(LANG)
    code   = Path(filepath).read_bytes()       # keeps encoding
    tree   = parser.parse(code)
    root   = tree.root_node

    feats = []

    def text(node):
        return robust_get_text(code, node, filepath)

    # ------------ recursive walk ------------------------------------
    def walk(node):
        if node.type == "class_declaration":
            cls_name     = None
            public_meths = []
            for child in node.children:
                if child.type == "identifier":
                    cls_name = text(child)
                elif child.type == "declaration_list":
                    # find `public` methods
                    for m in child.children:
                        if m.type == "method_declaration":
                            is_public = any(
                                ml.type == "modifier" and text(ml).strip() == "public"
                                for ml in m.children
                            )
                            if is_public:
                                meth_name = next(
                                    (mn for mn in m.children if mn.type == "identifier"),
                                    None
                                )
                                if meth_name:
                                    public_meths.append(text(meth_name))
            feats.append({
                "filepath": str(filepath),
                "lang": "csharp",
                "type": "class",
                "name": cls_name,
                "public_methods": public_meths,
                "source": text(node)
            })

        # Recurse
        for n in node.children:
            walk(n)

    walk(root)
    return feats

# Optional CLI:
if __name__ == "__main__":
    import sys, json, pathlib
    p = pathlib.Path(sys.argv[1])
    out = p.with_suffix(p.suffix + ".features.json")
    json.dump(extract_csharp_features(p), out.open("w"), indent=2)
    print("Wrote ->", out)