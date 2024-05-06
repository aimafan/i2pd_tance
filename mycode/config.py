import configparser
import os

# 创建一个配置解析器
config = configparser.RawConfigParser()

# 读取配置文件
config_path = "/app/mycode/config.ini"
config.read(config_path)