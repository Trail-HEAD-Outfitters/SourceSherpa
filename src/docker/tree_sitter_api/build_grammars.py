import argparse
from tree_sitter import build_library
parser = argparse.ArgumentParser()
parser.add_argument("grammars", nargs="+")
parser.add_argument("--out", required=True)
args = parser.parse_args()
build_library(args.out, args.grammars)
print("✅ built", args.out)
