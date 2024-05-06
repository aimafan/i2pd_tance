import subprocess
import configparser
import threading
from config import config
from push_mysql import DarknetDB
from kafka_cusumer import KafkaConsumerHandler
from del_lease import del_action
from get_log import logger

class MissingConfigError(Exception):
    """自定义异常类，用于表示缺少配置项的错误"""
    pass


def action(config_dic):
    executable_path = "/app/build/i2pd"       # 识别本地路径，去进行识别
    ntcp2_port = config_dic["ntcp2_port"]
    web_port = config_dic["web_port"]
    # log_file = config_dic["log_file"]
    num = config_dic["num"]
    
    kafka_server = config["kafka"]["bootstrap_servers"]
    kafka_topic = config["kafka"]["topic"]

    args = [f"--http.port", str(web_port), "--num", num, "--ntcp2.port", str(ntcp2_port), "--pidfile", "/root/." + num + "i2pd/i2pd.pid" , "--floodfill", "true", "--kafkaserver", kafka_server, "--kafkatopic", kafka_topic]
    
    logger.info(f"开启进程 " + executable_path + " " + " ".join(args))
    print(f"开启进程 " + executable_path + " " + " ".join(args))
    
    try:
        # 使用 subprocess.Popen 开启一个新进程
        process = subprocess.Popen([executable_path] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # 获取进程的输出和错误信息
        stdout, stderr = process.communicate()
        
        # 获取进程的返回码
        return_code = process.returncode
        # logger.info("程序输出：", stdout)
        # logger.error("程序错误信息：", stderr)
        # logger.error("程序返回码：", return_code)
        
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, process.args, output=stdout, stderr=stderr)
    
    except subprocess.CalledProcessError as e:
        logger.error("执行过程中出现错误:", e)
    except FileNotFoundError as e:
        logger.error("找不到可执行文件:", e)

def run_action(config):
    mysql_server = config["mysql"]["servers"]
    mysql_user = config["mysql"]["user_name"]
    mysql_password = config["mysql"]["password"]
    mysql_database = config["mysql"]["database"]
    mysql_port = config["mysql"]["port"]

    kafka_server = config["kafka"]["bootstrap_servers"]
    kafka_topic = config["kafka"]["topic"]

    mysql_db = DarknetDB(mysql_server, mysql_user, mysql_password, mysql_database, mysql_port)
    mysql_db.connect()
    print("mysql连接成功")
    kafka_consumer = KafkaConsumerHandler(kafka_server, kafka_topic, mysql_db)
    kafka_consumer.connect()
    print("kafka连接成功")


    # 开启一个kafka消费者进程，持续收集数据
    threads = []
    thread = threading.Thread(target=kafka_consumer.consume)
    threads.append(thread)
    thread.start()

    # 开启一个定时器，定期清除过期的Lease信息
    thread = threading.Thread(target=del_action)
    threads.append(thread)
    thread.start()

    logger.info(f"""
=========初始化完成，参数配置如下===========
[general]
log_path：{config['log']['log_path']}

[mysql]
server：{mysql_server}
port：{mysql_port}
username：{mysql_user}
password：******
database_name：{mysql_database}

[kafka]
server：{kafka_server}
topic：{kafka_topic}
=======================================
                """
                )
    print(f"""
=========初始化完成，参数配置如下===========
[general]
log_path：{config['log']['log_path']}

[mysql]
server：{mysql_server}
port：{mysql_port}
username：{mysql_user}
password：******
database_name：{mysql_database}

[kafka]
server：{kafka_server}
topic：{kafka_topic}
=======================================
                """
                )

    for section in config.sections():
        if "i2pd" in section:
            config_dic = {
                "ntcp2_port": 0,
                "web_port": 0,
                "num": "",
            }
            count = 0
            for key, value in config.items(section):
                if key in config_dic.keys():
                    config_dic[key] = value
                    count += 1
            if count < 3:
                raise MissingConfigError(f"{section} 缺少配置项")
            
            # 创建一个线程来执行 action 函数
            thread = threading.Thread(target=action, args=(config_dic,))
            threads.append(thread)
            thread.start()
    
    # 等待所有线程执行完毕
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    try:
        run_action(config)
    except MissingConfigError as e:
        logger.error("配置文件中缺少配置项错误:", e)