from fastapi import FastAPI, UploadFile, HTTPException
from tree_sitter import Parser, Language
import uvicorn, os
from typing import List
import traceback

LIB = os.getenv("TS_LIB", "my-languages.so")
LANG_CACHE = {}

def lang(name: str):
    if name not in LANG_CACHE:
        LANG_CACHE[name] = Language(LIB, name)
    return LANG_CACHE[name]

app = FastAPI()

@app.get("/logs")
def get_logs():
    try:
        with open("/srv/sidecar_error.log", "r") as f:
            return {"logs": f.read()}
    except Exception as e:
        return {"logs": f"Error reading log: {e}"}

@app.post("/parse")
async def parse(lang_id: str, file: UploadFile):
    supported = ["c_sharp","typescript","tsx","css","html","javascript","json"]  # removed 'yaml'
    if lang_id not in supported:
        raise HTTPException(400, f"lang_id {lang_id} not supported. Supported: {supported}")
    try:
        code = await file.read()
        parser = Parser(); parser.set_language(lang(lang_id))
        parser.parse(code)  # parse for side effects, but don't assign unused variable
        feat = {
            "filepath": file.filename,
            "lang": lang_id,
            "source": code.decode("utf-8", errors="replace")
        }
        return {"features": [feat]}
    except Exception as e:
        tb = traceback.format_exc()
        with open("/srv/sidecar_error.log", "a") as f:
            f.write(f"\n---\n{tb}\n")
        raise HTTPException(500, f"Internal error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
