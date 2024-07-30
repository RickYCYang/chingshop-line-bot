from loguru import logger

logger.add("logs/access_{time:YYYY-MM-DD}.log", rotation="00:00", retention="1 week")
