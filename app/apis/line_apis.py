from fastapi import APIRouter, Request

from linebot.v3.webhooks import MessageEvent

from app.services import line_services

router = APIRouter()


@router.post("/callback", tags=["Line"])
async def handle_callback(request: Request):
    events = await line_services.parse_line_events(request)
    for event in events:
        if isinstance(event, MessageEvent):
            await line_services.handle_message(event)
    return "OK"


# @router.post("/test", tags=["Line"])
# async def test(request: Request):
#     from app.services.google_sheet_services import google_sheet

#     data = google_sheet._GoogleSheet__get_all_records("test")
#     return data
