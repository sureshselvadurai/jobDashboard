from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

@app.post("/notify")
async def post_to_slack(request: Request):
    body = await request.json()
    text = body.get("text", "")

    if not text:
        return {"error": "Missing message text"}

    response = requests.post(SLACK_WEBHOOK_URL, json={"text": text})
    return {"status": response.status_code}
