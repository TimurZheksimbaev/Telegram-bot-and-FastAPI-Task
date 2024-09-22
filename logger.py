import logging

def create_logger(file, name):
    logger = logging.getLogger(name)
    file_handler = logging.FileHandler(file, mode="a", encoding="utf-8")
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "{levelname} - {name} - {asctime} - {pathname}{func} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

