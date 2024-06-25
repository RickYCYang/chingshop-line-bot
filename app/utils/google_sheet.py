from pydantic import BaseModel

# settings
scopes = ["https://spreadsheets.google.com/feeds"]
credential_file_path = "./app/credentials.json"

order_sheet_head = [
    "Group Name",
    "User",
    "User ID",
    "Timestamp",
    "Message",
    "Product",
    "Number",
]
product_sheet_head = ["Product", "ID", "Timestamp", "Price"]

order_sheet_name_prefix = "(Order)"
product_sheet_name_prefix = "(Product)"


class ProductPost(BaseModel):
    product: str
    id: str
