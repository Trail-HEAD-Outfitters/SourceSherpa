from fastapi import FastAPI, UploadFile, HTTPException
from tree_sitter import Parser, Language
import uvicorn, os
from typing import List

LIB = os.getenv("TS_LIB", "my-languages.so")
LANG_CACHE = {}

def lang(name: str):
    if name not in LANG_CACHE:
        LANG_CACHE[name] = Language(LIB, name)
    return LANG_CACHE[name]

app = FastAPI()

@app.post("/parse")
async def parse(lang_id: str, file: UploadFile):
    if lang_id not in ["c_sharp","typescript","tsx","sql"]:
        raise HTTPException(400, f"lang_id {lang_id} not supported")

    code = await file.read()
    parser = Parser(); parser.set_language(lang(lang_id))
    tree = parser.parse(code)

    # Very simple: emit one feature = whole file
    feat = {
        "filepath": file.filename,
        "lang": lang_id,
        "source": code.decode("utf-8", errors="replace")
    }
    return {"features": [feat]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
