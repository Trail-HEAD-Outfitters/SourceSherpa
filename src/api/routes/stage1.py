from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json, os
from src.prompts.loader import read
from src.api.bedrock_utils import call_bedrock
from src.config.settings import settings
from pymongo import MongoClient

router = APIRouter(prefix="/v1/stage1", tags=["stage-1"])

# --- (Reuse your Bedrock and Pydantic code from above) ---

class Stage1AnswerReq(BaseModel):
    question: str
    model_id: str
    max_context_docs: int = 50  # optional, default limit
    debug: bool = False  # allow UI/curl to specify debug

@router.post("/answer")
def full_stage1(payload: Stage1AnswerReq):
    # 1. Step 1: Get patterns from LLM
    patterns_prompt = (
        f"{read('mission_prefix')}\n\n"
        f"{read('dev_patterns_prompt')}\n\n"
        f"User Question: {payload.question}\n"
        "Return only a JSON array."
    )
    patterns_response = call_bedrock(patterns_prompt, payload.model_id)
    # Defensive: Parse out JSON array from code block if needed
    patterns_json = patterns_response
    try:
        # Try to extract JSON array if inside markdown
        import re
        match = re.search(r'```json\n([\s\S]+?)\n```', patterns_response)
        if match:
            patterns_json = match.group(1)
        patterns = json.loads(patterns_json)
    except Exception as ex:
        raise HTTPException(400, f"Failed to parse patterns JSON: {ex}\n{patterns_response}")

    # 2. Step 2: Get Mongo filter from LLM
    filter_prompt = (
        f"{read('mission_prefix')}\n\n"
        f"{read('mongo_schema_structure')}\n\n"
        f"User Question: {payload.question}\n"
        f"LLM File Patterns/Globs: {json.dumps(patterns)}\n\n"
        "Return only a valid JSON filter object."
    )
    filter_response = call_bedrock(filter_prompt, payload.model_id)
    try:
        # Remove code block if present
        match = re.search(r'```json\n([\s\S]+?)\n```', filter_response)
        filter_json = match.group(1) if match else filter_response
        mongo_filter = json.loads(filter_json)
    except Exception as ex:
        raise HTTPException(400, f"Failed to parse filter JSON: {ex}\n{filter_response}")

    # 3. Step 3: Query Mongo
    uri = settings.mongodb_uri
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    coll = client["code_routing"]["features"]
    context_docs = list(coll.find(mongo_filter).limit(payload.max_context_docs))

    # 4. Step 4: Compose context for LLM final answer
    # Summarize context docs if there are many
    context_summary = ""
    for d in context_docs[:10]:  # Limit to 10 for context; you can expand if needed
        snippet = d.get("value") or d.get("source_file") or str(d)
        context_summary += f"- {snippet}\n"

    # Extract codebase nickname and product name from filter_response if present
    codebase_nickname = None
    product_name = None
    if isinstance(filter_response, dict):
        codebase_nickname = filter_response.get("codebase_nickname")
        product_name = filter_response.get("product_name")
    # fallback: try mongo_filter
    if not codebase_nickname and isinstance(mongo_filter, dict):
        codebase_nickname = mongo_filter.get("codebase_nickname")
    if not product_name and isinstance(mongo_filter, dict):
        product_name = mongo_filter.get("product_name")
    # fallback: generic
    if not codebase_nickname:
        codebase_nickname = "the codebase"
    if not product_name:
        product_name = "the product"

    # Load the new expert prompt template
    with open(os.path.join(os.path.dirname(__file__), '../../prompts/final_answer.md'), 'r') as f:
        expert_prompt_template = f.read()

    # Fill in the template variables
    final_prompt = expert_prompt_template.format(
        codebase_nickname=codebase_nickname,
        product_name=product_name,
        question=payload.question,
        patterns_json=json.dumps(patterns, indent=2),
        context_summary=context_summary.strip()
    )

    answer = call_bedrock(final_prompt, payload.model_id)

    response = {
        "question": payload.question,
        "patterns": patterns,
        "mongo_filter": mongo_filter,
        "context_docs_count": len(context_docs),
        "context_docs_preview": context_docs[:3],  # return first 3 for UI/inspection
        "llm_answer": answer,
    }
    if payload.debug:
        response["_debug"] = {
            "patterns_prompt": patterns_prompt,
            "patterns_response": patterns_response,
            "filter_prompt": filter_prompt,
            "filter_response": filter_response,
            "final_prompt": final_prompt,
            "final_response": answer,
        }
    return response