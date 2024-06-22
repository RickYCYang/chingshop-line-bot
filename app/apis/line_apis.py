from fastapi import APIRouter, Request

from linebot.v3.webhooks import MessageEvent

from app.services import line

router = APIRouter()


@router.post("/callback", tags=["Line"])
async def handle_callback(request: Request):
    events = await line.parse_line_events(request)
    for event in events:
        if isinstance(event, MessageEvent):
            await line.handle_message(event)
    return "OK"
