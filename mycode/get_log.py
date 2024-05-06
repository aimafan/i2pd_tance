import logging
import logging.handlers
import os
from config import config


# 配置日志基本设置
def setup_logging(log_path="defult.log", maxMB=500, backupCount=3):
    # 创建一个logger
    logger = logging.getLogger(log_path.split("/")[-1].split(".")[0])
    logger.setLevel(logging.DEBUG)  # 可以根据需要设置不同的日志级别

    # 创建一个handler，用于写入日志文件
    log_file = log_path

    # 用于写入日志文件，当文件大小超过500MB时进行滚动
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=maxMB * 1024 * 1024, backupCount=backupCount
    )
    file_handler.setLevel(logging.DEBUG)

    # 创建一个handler，用于将日志输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)

    # 定义handler的输出格式
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 给logger添加handler
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logging(config["log"]["log_path"], int(config['log']['maxMB']), int(config['log']['backupCount']))

#############################################
## use example
# # 获取配置好的logger
# logger = getlog.setup_logging(file_name)

# # 记录日志
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')
#############################################
