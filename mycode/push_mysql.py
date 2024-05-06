import mysql.connector

import datetime
from get_log import logger
from lock import lock

def convert_to_mysql_datetime(timestamp):
    # Assuming the input timestamp is in milliseconds
    # Convert it to seconds by dividing by 1000
    timestamp_seconds = timestamp / 1000

    # Create a datetime object from the timestamp
    dt_object = datetime.datetime.fromtimestamp(timestamp_seconds)

    # Format the datetime object as a MySQL-compatible string
    mysql_datetime = dt_object.strftime('%Y-%m-%d %H:%M:%S')

    return mysql_datetime


class DarknetDB:
    def __init__(self, host, user, password, database, port):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                connection_timeout=300
            )
            self.cursor = self.conn.cursor()
            with lock:
                self.create_database()
                self.create_routerinfo_table()
                self.create_leasesets_table()
            logger.info("已经成功连接到mysql服务器")
        except mysql.connector.Error as error:
            logger.error(f"Error connecting to MySQL database: {error}")

    def create_database(self):
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
        self.cursor.execute(f"USE {self.database}")

    def create_routerinfo_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS RouterInfo ("
                       "hash VARCHAR(64) PRIMARY KEY, "
                       "isFFpeers BOOLEAN, "
                       "caps VARCHAR(6), "
                       "version VARCHAR(6), "
                       "netId VARCHAR(2), "
                       "published_time DATETIME, "
                       "firsttime   DATETIME, "
                       "updatetime DATETIME, "
                       "crytokeytype VARCHAR(50), "
                       "signingkeytype VARCHAR(25), "
                       "NTCP2_ipv4 VARCHAR(20), "
                       "NTCP2_ipv4_port INT, "
                       "NTCP2_s VARCHAR(64), "
                       "NTCP2_i VARCHAR(32), "
                       "NTCP2_ipv6 VARCHAR(45), "
                       "NTCP2_ipv6_port INT, "
                       "SSU_ipv4 VARCHAR(20), "
                       "SSU_ipv4_port INT, "
                       "SSU_ipv6 VARCHAR(45), "
                       "SSU_ipv6_port INT"
                       ")")
        
    def create_leasesets_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS LeaseSets ("
                      "hash VARCHAR(128) PRIMARY KEY, "
                      "encryption_type VARCHAR(64), "
                      "expiration_time DATETIME, "
                      "storage_type VARCHAR(50), "
                      "first_time DATETIME, "
                      "update_time DATETIME"
                      ")")
        
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Leases ("
                      "lease_id INT AUTO_INCREMENT PRIMARY KEY, "
                      "router_hash VARCHAR(128), "
                      "gateway_address VARCHAR(128), "
                      "tunnel_id VARCHAR(128), "
                      "first_time DATETIME, "
                      "expiration_time DATETIME, "
                      "FOREIGN KEY (router_hash) REFERENCES LeaseSets(hash)"
                      ")")

   
        
    def close(self):
        if self.conn:
            self.conn.close()
            print("MySQL connection closed")

    def add_routerinfo(self, routerinfo_dic):
        # 构建插入语句
        # + 记录首次发现时间
        public = convert_to_mysql_datetime(routerinfo_dic["public_time"])
        update = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        routerinfo_dic["public_time"] = public
        routerinfo_dic["update_time"] = update
        routerinfo_dic["first_time"] = update

        insert_query = ("INSERT INTO RouterInfo "
                        "(hash, isFFpeers, caps, version, netId, published_time, firsttime, updatetime, crytokeytype, signingkeytype, "
                        "NTCP2_ipv4, NTCP2_ipv4_port, NTCP2_s, NTCP2_i, NTCP2_ipv6, NTCP2_ipv6_port, "
                        "SSU_ipv4, SSU_ipv4_port, SSU_ipv6, SSU_ipv6_port) "
                        "VALUES (%(hexString)s, %(is_floodfill)s, %(caps)s, %(version)s, %(netid)s, "
                        "%(public_time)s, %(first_time)s, %(update_time)s, %(cryptokeytype)s, %(signingkeytype)s, %(ntcp2_ipv4)s, "
                        "%(ntcp2_port)s, %(ntcp2_s)s, %(ntcp2_i)s, %(ntcp2_ipv6)s, %(ntcp2_ipv6_port)s, "
                        "%(ssu_ipv4)s, %(ssu_ipv4_port)s, %(ssu_ipv6)s, %(ssu_ipv6_port)s) "
                        "ON DUPLICATE KEY UPDATE "
                        "hash=VALUES(hash), "
                        "isFFpeers=VALUES(isFFpeers), "
                        "caps=VALUES(caps), "
                        "version=VALUES(version), "
                        "netId=VALUES(netId), "
                        "published_time=VALUES(published_time), "
                        "updatetime=VALUES(updatetime), "
                        "crytokeytype=VALUES(crytokeytype), "
                        "signingkeytype=VALUES(signingkeytype), "
                        "NTCP2_ipv4=VALUES(NTCP2_ipv4), "
                        "NTCP2_ipv4_port=VALUES(NTCP2_ipv4_port), "
                        "NTCP2_s=VALUES(NTCP2_s), "
                        "NTCP2_i=VALUES(NTCP2_i), "
                        "NTCP2_ipv6=VALUES(NTCP2_ipv6), "
                        "NTCP2_ipv6_port=VALUES(NTCP2_ipv6_port), "
                        "SSU_ipv4=VALUES(SSU_ipv4), "
                        "SSU_ipv4_port=VALUES(SSU_ipv4_port), "
                        "SSU_ipv6=VALUES(SSU_ipv6), "
                        "SSU_ipv6_port=VALUES(SSU_ipv6_port)")

        # 执行插入操作
        self.cursor.execute(insert_query, routerinfo_dic)
        self.conn.commit()
        logger.debug(f"RouterInfo信息存储成功，Router Hash为 {routerinfo_dic['hexString']}")

    def add_leaseset(self, leaseset_dic):
        # 首次发现时间
        update = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        leaseset_dic["update_time"] = update
        leaseset_dic["first_time"] = update
        leaseset_dic['expiration_time'] = convert_to_mysql_datetime(leaseset_dic['expiration_time'])

        lease_set_query = ("INSERT INTO LeaseSets (hash, encryption_type, expiration_time, storage_type, first_time, update_time) VALUES (%s, %s, %s, %s, %s, %s)"
        "ON DUPLICATE KEY UPDATE "
        "hash=VALUES(hash), "
        "encryption_type=VALUES(encryption_type), "
        "expiration_time=VALUES(expiration_time), "
        "storage_type=VALUES(storage_type), "
        "update_time=VALUES(update_time) ")
        lease_set_values = (leaseset_dic["hash"], leaseset_dic["encryption_type"], leaseset_dic["expiration_time"], leaseset_dic["storage_type"], leaseset_dic["first_time"], leaseset_dic["update_time"])
        self.cursor.execute(lease_set_query, lease_set_values)
        count = 0
        # 插入 Lease 数据
        for lease_entry in leaseset_dic["leases"]:
            lease_entry["first_time"] = update
            count += 1
            lease_entry["expiration_time"] = convert_to_mysql_datetime(lease_entry["expiration_time"])
            lease_query = "INSERT INTO Leases (gateway_address, tunnel_id, first_time, expiration_time, router_hash) VALUES (%s, %s, %s, %s, %s)"
            lease_values = (lease_entry["gateway_address"], lease_entry["tunnel_id"], lease_entry["first_time"] ,lease_entry["expiration_time"], leaseset_dic["hash"])
            self.cursor.execute(lease_query, lease_values)
        self.conn.commit()
        logger.debug(f"LeaseSet信息存储成功，Router Hash为 {leaseset_dic['hash']}，共存入 {count} 条Lease数据")

    def delete_expired_rows(self):
        sql_query = "DELETE FROM Leases WHERE expiration_time < NOW()"
        self.cursor.execute(sql_query)
        self.conn.commit()
        logger.info(f"删除过期的Lease条目")


    def __del__(self):
        self.close()


# 使用示例
if __name__ == "__main__":
    mysql_db = DarknetDB("142.171.227.116", "root", "aimafan", "test")
    mysql_db.connect()
    routerinfo_dic = {
        "hexString": 'FsYEqV8qantJZc96IRo2CETlC3eEj~FZjQwqBC3DchU=',
        "is_floodfill": True,
        "caps": "RIF",
        "version": "9.61",
        "netid": "2",
        "public_time": 1709899730888,
        "cryptokeytype": "ECIES_X25519_AEAD",
        "signingkeytype": "EDDSA_SHA512_ED25519",
        "ntcp2_ipv4": "73.53.99.121",
        "ntcp2_port": 18024,
        "ntcp2_s": "FsYEqV8qantJZc96IRo2CETlC3eEj~FZjQwqBC3DchU=",
        "ntcp2_i": "AUdGUI428hw4JBLMNnV4zA",
        "ntcp2_ipv6": " ",
        "ntcp2_ipv6_port": 0,
        "ssu_ipv4": "73.53.99.121",
        "ssu_ipv4_port": 18024,
        "ssu_ipv6": " ",
        "ssu_ipv6_port": 0
    }
    public = convert_to_mysql_datetime(routerinfo_dic["public_time"])
    uptedate = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    routerinfo_dic["public_time"] = public
    routerinfo_dic["update_time"] = uptedate

    mysql_db.add_routerinfo(routerinfo_dic)

   