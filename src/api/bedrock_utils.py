import json
import boto3

def call_bedrock(prompt: str, model_id: str) -> str:
    bedrock_profile = boto3.Session(profile_name='bedrock')
    bedrock = bedrock_profile.client(service_name='bedrock-runtime', region_name='us-east-1')
    payload = {
        "inferenceConfig": {
            "max_new_tokens": 1000
        },
        "messages": [
            {
                "role": "user",
                "content": [
                    {"text": prompt}
                ]
            }
        ]
    }
    resp = bedrock.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload).encode("utf-8")
    )
    out = resp["body"].read().decode("utf-8")
    return out
