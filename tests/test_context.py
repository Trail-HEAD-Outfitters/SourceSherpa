from src.context.block import ContextBlock

def test_block_to_dict():
    block = ContextBlock(
        repo="repo",
        pattern="Controller",
        filepath="src/Foo.cs",
        metadata={"desc": "desc"},
        snippet="snippet"
    )
    d = block.to_dict()
    assert d["repo"] == "repo"
