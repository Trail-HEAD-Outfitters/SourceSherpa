from sourcesherpa.context.block import ContextBlock

def extract_dummy():
    # Replace this with your real codebase logic!
    block = ContextBlock(
        repo="dummy-repo",
        pattern="Controller",
        filepath="src/Controllers/FooController.cs",
        metadata={"desc": "Sample Controller"},
        snippet="class FooController { ... }"
    )
    return [block]
