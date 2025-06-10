from pathlib import Path

def robust_get_text(code: bytes, node, filepath: str, max_bytes: int = 50_000) -> str:
    """
    Slice `code[start:end]` and decode as UTF-8.
    Falls back to a placeholder if bytes are binary or huge.
    """
    try:
        segment = code[node.start_byte : node.end_byte]
        if len(segment) > max_bytes:
            return f"<large-slice in {Path(filepath).name}  {node.start_point}-{node.end_point}>"
        return segment.decode("utf-8", errors="replace")
    except Exception:
        return f"<binary-slice in {Path(filepath).name}>"