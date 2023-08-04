from fastapi import (
    FastAPI,
    HTTPException,
    Response,
)
from fastapi.middleware.cors import CORSMiddleware
from coar_notify_validator.validate import validate

from models import Notification
from slack import post_slack_message


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthcheck")
async def health_check():
    return {"status": "ok"}


@app.options("/inbox")
async def read_inbox_options():
    return Response(headers={"Accept-Post": "application/ld+json"})


@app.post("/inbox")
async def add_notification(notification: Notification):
    conforms, errors = validate(notification)

    if not conforms:
        raise HTTPException(status_code=400, detail=errors)

    post_slack_message(payload=notification)

    return Response(status_code=201, content="ok")
