from __future__ import annotations
from functools import lru_cache
from pathlib import Path
try:
    from tree_sitter_languages import get_language as _wheel_get_language
    _WHEEL = True
except ModuleNotFoundError:
    _WHEEL = False
    from tree_sitter import Language
    LIB_PATH = Path(__file__).resolve().parents[2] / "build" / "my-languages.so"
    if not LIB_PATH.exists():
        raise FileNotFoundError(
            "Neither tree_sitter_languages wheel nor build/my-languages.so present."
        )
    @lru_cache(maxsize=None)
    def _lib_get_language(lang: str):
        return Language(str(LIB_PATH), lang)

@lru_cache(maxsize=None)
def get_language(lang: str):
    """Return a tree_sitter.Language for `lang`."""
    return _wheel_get_language(lang) if _WHEEL else _lib_get_language(lang)