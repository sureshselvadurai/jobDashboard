import logging

from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/notify")
async def post_to_slack(request: Request):
    body = await request.json()
    text = body.get("text", "")

    if not text:
        return {"error": "Missing message text"}
    logger.info(f"SLACK_WEBHOOK_URL: {SLACK_WEBHOOK_URL}")


    response = requests.post(SLACK_WEBHOOK_URL, json={"text": text})
    return {"status": response.status_code}
