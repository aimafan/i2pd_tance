import time
from push_mysql import DarknetDB
from config import config
from lock import lock



def del_action():
    mysql_server = config["mysql"]["servers"]
    mysql_user = config["mysql"]["user_name"]
    mysql_password = config["mysql"]["password"]
    mysql_database = config["mysql"]["database"]
    mysql_port = config["mysql"]["port"]

    mysql_db = DarknetDB(mysql_server, mysql_user, mysql_password, mysql_database, mysql_port)
    mysql_db.connect()
    while(True):
        with lock:
            mysql_db.delete_expired_rows()
        time.sleep(int(config["mysql"]["gap_time_second"]))
