from logging import Logger, StreamHandler, Formatter
from decouple import config

def setup_logger():
    streamHandler = StreamHandler()
    formatter = Formatter(
        fmt="%(levelname)s %(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(message)s"
    )

    streamHandler.setFormatter(formatter)
    logger = Logger('Flow_Manager')
    if config("env", cast=str, default="dev") == "dev":
        logger.setLevel(10) # debug and above
    else:
        logger.setLevel(20) # info and above
    logger.handlers = []
    logger.addHandler(streamHandler)

    return logger

log = setup_logger()
