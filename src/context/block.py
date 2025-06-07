from typing import Dict, Any

class ContextBlock:
    def __init__(self, repo: str, pattern: str, filepath: str, metadata: Dict[str, Any], snippet: str = None):
        self.repo = repo
        self.pattern = pattern
        self.filepath = filepath
        self.metadata = metadata
        self.snippet = snippet

    def to_dict(self):
        return {
            "repo": self.repo,
            "pattern": self.pattern,
            "filepath": self.filepath,
            "metadata": self.metadata,
            "snippet": self.snippet
        }
