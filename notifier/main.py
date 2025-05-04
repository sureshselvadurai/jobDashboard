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
    return {"status": "ok", "color" : "green"}


@app.post("/notify")
async def post_to_slack(request: Request):
    try:
        body = await request.json()
        text = body.get("text", "")

        if not text:
            return {"error": "Missing message text"}

        logger.info(f"Sending to Slack: {text}")
        logger.info(f"SLACK_WEBHOOK_URL: {SLACK_WEBHOOK_URL}")

        response = requests.post(SLACK_WEBHOOK_URL, json={"text": text})

        if response.status_code != 200:
            logger.error(f"Slack returned {response.status_code}: {response.text}")
            return {"error": f"Slack error {response.status_code}", "details": response.text}

        return {"status": "sent"}

    except Exception as e:
        logger.exception("Failed to send message to Slack")
        return {"error": str(e)}
