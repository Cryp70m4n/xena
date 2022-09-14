import logging

def setup_logger(logger_name, log_file, level=logging.DEBUG):
    log = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    fileHandler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    fileHandler.setFormatter(formatter)

    log.setLevel(level)
    log.addHandler(fileHandler)
