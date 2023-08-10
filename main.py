from fastapi import (
    BackgroundTasks,
    Body,
    FastAPI,
    HTTPException,
    Response,
)
from fastapi.middleware.cors import CORSMiddleware

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

    background_tasks.add_task(post_slack_message, payload=payload)

    return Response(status_code=201, content="ok")
