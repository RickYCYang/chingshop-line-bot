from datetime import datetime


def get_current_yyyymm():
    current_date = datetime.now()
    year_month_string = current_date.strftime("%Y%m")
    return year_month_string


def timestamp_to_datetime(timestamp):
    # Convert milliseconds to seconds
    timestamp_seconds = timestamp / 1000
    # Convert timestamp to datetime object
    dt_object = datetime.fromtimestamp(timestamp_seconds)
    # Format datetime object as "yyyy/mm/dd hh:mm:ss"
    formatted_datetime = dt_object.strftime("%Y/%m/%d %H:%M:%S")
    return formatted_datetime
