from pathlib import Path

PROMPT_DIR = Path(__file__).parent

def read(name: str) -> str:
    """Read a prompt Markdown file by stem, e.g. read('mission_prefix')."""
    return (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8").strip()