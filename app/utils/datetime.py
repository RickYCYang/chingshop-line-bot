from datetime import datetime, timedelta


def get_yyyymm(month_offset=0):
    # Get current date
    current_date = datetime.now()

    # Calculate the new month
    new_month = current_date.month + month_offset
    new_year = current_date.year + (new_month - 1) // 12
    new_month = (new_month - 1) % 12 + 1

    # Format the result as yyyymm
    result = f"{new_year}{new_month:02}"

    return result


def timestamp_to_datetime(timestamp):
    # Convert milliseconds to seconds
    timestamp_seconds = timestamp / 1000
    # Convert timestamp to datetime object
    dt_object = datetime.fromtimestamp(timestamp_seconds)
    # Format datetime object as "yyyy/mm/dd hh:mm:ss"
    formatted_datetime = dt_object.strftime("%Y/%m/%d %H:%M:%S")
    return formatted_datetime
