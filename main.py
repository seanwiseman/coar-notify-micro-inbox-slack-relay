import json

from fastapi import (
    BackgroundTasks,
    Body,
    FastAPI,
    HTTPException,
    Response,
)
from fastapi.middleware.cors import CORSMiddleware

from db import notifications
from db.models import Notification
from slack import post_slack_message
from validation import validate_notification


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
async def add_notification(background_tasks: BackgroundTasks, payload: dict = Body(...)):
    conforms, errors = validate_notification(payload)

    if not conforms:
        raise HTTPException(status_code=400, detail=errors)

    await notifications.create(payload)

    background_tasks.add_task(post_slack_message, payload=payload)

    return Response(status_code=201, content="ok")


@app.get("/inbox/{notification_id}", response_model=Notification)
async def read_notification(notification_id: str):
    notification = await notifications.get_by_id(notification_id)

    if notification:
        return Response(
            headers={"content-type": "application/ld+json"},
            content=json.dumps(notification, default=str),
        )

    raise HTTPException(status_code=404, detail="Notification not found")
