from pydantic.v1 import StrictInt, StrictStr

import gspread
from gspread import Worksheet
from gspread.exceptions import WorksheetNotFound
from oauth2client.service_account import ServiceAccountCredentials
from loguru import logger

from app.settings import GOOGLE_SHEET

from app.utils.datetime import get_current_yyyymm, timestamp_to_datetime

scopes = ["https://spreadsheets.google.com/feeds"]
credential_file_path = "./app/credentials.json"
order_sheet_head = [
    "Group Name",
    "User",
    "User ID",
    "Timestamp",
    "Message",
    "Reply Message Id",
]


class GoogleSheet:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credential_file_path, scopes
        )
        client = gspread.authorize(credentials)
        self.excel = client.open_by_key(GOOGLE_SHEET)

    def __get_sheet(self, sheet_name):
        try:
            return self.excel.worksheet(sheet_name)
        except WorksheetNotFound as e:
            logger.error(f"worksheet {sheet_name} not found, create a new sheet")
            sheet = self.__add_sheet(sheet_name)
            sheet.append_row(order_sheet_head)
            return sheet

    def __get_all_records(self, sheet_name):
        return self.excel.worksheet(sheet_name).get_all_records()

    def __add_sheet(self, sheet_name):
        sheet = self.excel.add_worksheet(sheet_name, 0, 0)
        return sheet

    def append_user_message(
        self,
        group_name: str,
        user_id: str,
        user_name: str,
        message: str,
        quoted_message_id: str,
        timestamp: StrictInt,
    ):
        """get current datetime"""
        date_time = timestamp_to_datetime(timestamp)
        current_yyyymm = get_current_yyyymm()

        """append row"""
        sheet = self.__get_sheet(current_yyyymm)
        row = [
            group_name,
            user_name,
            user_id,
            date_time,
            message,
            quoted_message_id,
        ]
        sheet.append_row(values=row)


google_sheet = GoogleSheet()
