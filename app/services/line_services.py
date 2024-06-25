# import requests
import asyncio
from loguru import logger
from fastapi import Request, HTTPException

from linebot.v3.messaging import UserProfileResponse
from linebot.v3.messaging import ReplyMessageRequest, TextMessage
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent

from app.services.google_sheet_services import google_sheet

from app.settings import LINE_CHANNEL_ACCESS_TOKEN, parser, line_bot_api

from app.utils.datetime import timestamp_to_datetime
from app.utils.line import manager_ids, product_keywords


headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
}


async def get_user_profile(user_id: str) -> UserProfileResponse:
    try:
        user_profile = await line_bot_api.get_profile(user_id)
        logger.info(f"user_profile - {user_profile}")
        return user_profile
    except Exception as e:
        logger.error(e)
        return "親，我們還不熟讓我們更近一步添加好友"


async def parse_line_events(request: Request):
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = await request.body()
    body = body.decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return events


def is_product_post(post: str) -> bool:
    for keyword in product_keywords:
        if keyword in post:
            return True

    return False


async def handle_manager_message(event: MessageEvent, date_time: str):
    """extract user and group's info"""
    # group_id, user_id = event.source.group_id, event.source.user_id
    logger.info(f"receive manager {event=}")

    post = event.message.text
    if not is_product_post(post):
        return

    google_sheet.add_product(post=post, post_id=event.message.id, date_time=date_time)


async def handle_cust_message(event: MessageEvent, user_id: str, date_time: str):
    logger.info(f"receive customer {event=}")

    group_id = event.source.group_id
    user_profile, group_summary = await asyncio.gather(
        line_bot_api.get_profile(user_id),
        line_bot_api.get_group_summary(group_id),
    )

    logger.info(f"{user_profile=}")
    logger.info(f"{group_summary=}")

    """ extract and process message """
    message = event.message.text
    quoted_message_id = event.message.quoted_message_id

    """ process google sheet """
    google_sheet.add_order(
        group_name=group_summary.group_name,
        user_id=user_profile.user_id,
        user_name=user_profile.display_name,
        message=message,
        quoted_message_id=quoted_message_id,
        date_time=date_time,
    )

    # await reply_cust_message(event=event, user_name=user_profile.display_name)


async def reply_cust_message(event: MessageEvent, user_name: str):
    reply_message = f"Hello {user_name} $ , 我們收到你的訊息 '{event.message.text}' 摟"
    await line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(
                    text=reply_message,
                    emojis=[
                        {
                            "index": reply_message.index("$"),
                            "productId": "5ac1bfd5040ab15980c9b435",
                            "emojiId": "001",
                        }
                    ],
                )
            ],
            # quote_token=event.message.quote_token,
        ),
    )


async def handle_message(event: MessageEvent):
    try:
        logger.info(f"{event=}")
        if event.type != "message":
            return

        """ extract user and group's info """
        user_id = event.source.user_id
        date_time = timestamp_to_datetime(timestamp=event.timestamp)

        """ post by manager """
        if user_id in manager_ids:
            await handle_manager_message(event=event, date_time=date_time)
            return

        """ post by users """
        await handle_cust_message(event=event, user_id=user_id, date_time=date_time)
    except Exception as e:
        logger.error(str(e))
