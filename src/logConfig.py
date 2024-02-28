###################
# SETUP LOGGER
###################

import logging
import os


def init_logger(path="data_diet.log"):
    filemode = "a"
    # create logger
    if not os.path.exists("logs"):
        os.makedirs("logs")
        filemode = "w"

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
        filename="logs/" + path,
        filemode=filemode,
    )

    # create console handler and set level to debug
    # best for development or debugging
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)

    # add ch to logger
    logger.handlers.clear()
    logger.addHandler(consoleHandler)
    return logger
