from fastapi import FastAPI, Request
import os
from slack_sdk.webhook import WebhookClient
import requests

app = FastAPI()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/notify")
async def post_to_slack(request: Request):
    body = await request.json()
    text = body.get("text", "")

    if not text:
        return {"error": "Missing message text"}

    webhook = WebhookClient(SLACK_WEBHOOK_URL)

    webhook.send(
        text=(
            f"{text}"
        )
    )
    return {"status": SLACK_WEBHOOK_URL}
