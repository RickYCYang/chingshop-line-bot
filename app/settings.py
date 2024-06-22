from decouple import config

from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
)

""" env vars """
LINE_CHANNEL_ACCESS_TOKEN = config("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = config("LINE_CHANNEL_SECRET")
GOOGLE_SHEET = config("GOOGLE_SHEET_ID")

""" line settings """
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(LINE_CHANNEL_SECRET)
async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
