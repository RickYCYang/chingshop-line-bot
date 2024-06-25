import gspread
from gspread import Worksheet
from gspread.exceptions import WorksheetNotFound
from oauth2client.service_account import ServiceAccountCredentials
from loguru import logger

from app.settings import GOOGLE_SHEET

from app.utils.datetime import get_yyyymm
from app.utils.google_sheet import (
    scopes,
    credential_file_path,
    order_sheet_head,
    product_sheet_head,
    order_sheet_name_prefix,
    product_sheet_name_prefix,
    ProductPost,
)


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

    def __get_sheet(self, sheet_name, sheet_head) -> Worksheet:
        """_summary_

        Args:
            sheet_name (_type_): _description_
            sheet_head (_type_): _description_

        Returns:
            Worksheet: _description_
        """
        try:
            return self.excel.worksheet(sheet_name)
        except WorksheetNotFound as e:
            logger.error(f"worksheet {sheet_name} not found, create a new sheet")
            sheet = self.__add_sheet(sheet_name)
            sheet.append_row(sheet_head)
            return sheet

    def __get_all_records(self, sheet_name):
        try:
            return self.excel.worksheet(sheet_name).get_all_records()
        except Exception as e:
            logger.error(str(e))
            return []

    def __add_sheet(self, sheet_name) -> Worksheet:
        sheet = self.excel.add_worksheet(sheet_name, 0, 0)
        return sheet

    def __get_sheet_name(self, yyyymm: str, prefix: str):
        return f"{prefix} {yyyymm}"

    def add_product(
        self,
        post: str,
        post_id: str,
        date_time: str,
    ):
        # get current datetime
        current_yyyymm = get_yyyymm()

        # get product sheet
        product_sheet_name = self.__get_sheet_name(
            current_yyyymm, product_sheet_name_prefix
        )
        product_sheet = self.__get_sheet(product_sheet_name, product_sheet_head)
        product_row: list[str] = [post, post_id, date_time]
        product_sheet.append_row(values=product_row)

    def __parse_cust_order_number(self, message: str) -> str:
        try:
            if "+" in message:
                return message[message.index("+") + 1 :]
            return message[message.index("加") + 1 :]
        except ValueError:
            logger.warning(f"symbol '+' not found {message=}")
            return ""

    def __get_all_product_posts(self) -> list[ProductPost]:
        """prepare product sheet names"""
        cur_yyyymm, last_yyyymm = get_yyyymm(), get_yyyymm(-1)
        cur_yyyymm_sheet_name = self.__get_sheet_name(
            yyyymm=cur_yyyymm, prefix=product_sheet_name_prefix
        )
        last_yyyymm_sheet_name = self.__get_sheet_name(
            yyyymm=last_yyyymm, prefix=product_sheet_name_prefix
        )

        products = []
        for sheet_name in [cur_yyyymm_sheet_name, last_yyyymm_sheet_name]:
            for record in self.__get_all_records(sheet_name):
                product = record.get("Product")
                id = record.get("ID")
                if id is None:
                    continue
                products.append(ProductPost(product=product, id=str(id)))
        logger.info(f"{products=}")
        return products

    def __parse_cust_message(self, message: str, quoted_message_id: str):
        product, order_number = "", ""
        order_number = self.__parse_cust_order_number(message)

        if quoted_message_id is None:
            return product, order_number

        logger.info(f"{quoted_message_id=} {type(quoted_message_id)=}")

        products = self.__get_all_product_posts()

        logger.info(f"{products[0].id=} {type(products[0].id)=}")
        for item in products:
            if quoted_message_id == item.id:
                product = item.product
                break

        return product, order_number

    def add_order(
        self,
        group_name: str,
        user_id: str,
        user_name: str,
        message: str,
        quoted_message_id: str,
        date_time: str,
    ):
        # get current datetime
        current_yyyymm = get_yyyymm()

        # parse related fields from message
        product, order_number = self.__parse_cust_message(
            message=message, quoted_message_id=quoted_message_id
        )

        # get order sheet
        order_sheet_name = self.__get_sheet_name(
            current_yyyymm, order_sheet_name_prefix
        )
        order_sheet = self.__get_sheet(order_sheet_name, order_sheet_head)

        # add record
        order_row = [
            group_name,
            user_name,
            user_id,
            date_time,
            message,
            product,
            order_number,
        ]
        order_sheet.append_row(values=order_row)


google_sheet = GoogleSheet()
