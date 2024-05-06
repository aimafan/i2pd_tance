from confluent_kafka import Consumer, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic
from push_mysql import DarknetDB
import time
from get_log import logger
from lock import lock

class KafkaConsumerHandler:
    def __init__(self, server, topic, mysql_db):
        self.bootstrap_servers = server
        self.topic = topic
        self.mysql_db = mysql_db
        self.group_id = "90"
        self.auto_offset_reset = "latest"  # Start consuming from the current position, ignoring old messages (real-time consumption)

    def connect(self):
        consumer_config = {
            "bootstrap.servers": self.bootstrap_servers,
            "group.id": self.group_id,
            "auto.offset.reset": self.auto_offset_reset
        }

        try:
            # admin_client = AdminClient({
            #     "bootstrap.servers": self.bootstrap_servers
            # })

            # topic_list = []
            # topic_list.append(NewTopic(self.topic, 1, 1))

            # fs = admin_client.create_topics(topic_list)


            time.sleep(0.3)
            self.consumer = Consumer(consumer_config)

            self.consumer.subscribe([self.topic])
        except Exception as e:
            print("kafka error " + str(e))
        
        logger.info("已经成功连接到Kafka服务器")

    def _handle_routerinfo(self, fields):
        is_floodfill = fields[2] == "1"
        routerinfo_dic = {
            "hexString": fields[1],
            "is_floodfill": is_floodfill,
            "caps": fields[3],
            "version": fields[4],
            "netid": fields[5],
            "public_time": int(fields[6]),
            "cryptokeytype": fields[7],
            "signingkeytype": fields[8],
            "ntcp2_ipv4": fields[9],
            "ntcp2_port": int(fields[10]),
            "ntcp2_s": fields[11],
            "ntcp2_i": fields[12],
            "ntcp2_ipv6": fields[13],
            "ntcp2_ipv6_port": int(fields[14]),
            "ssu_ipv4": fields[15],
            "ssu_ipv4_port": int(fields[16]),
            "ssu_ipv6": fields[17],
            "ssu_ipv6_port": int(fields[18])
        }
        logger.debug(f"接收到routerinfo信息，router hash为 {routerinfo_dic['hexString']}")
        with lock:
            self.mysql_db.add_routerinfo(routerinfo_dic)

    def _handle_leasesets(self, fields):
        leaseset_dic = {
            "hash" : fields[1],
            "encryption_type": fields[2],
            "expiration_time" : int(fields[3]),
            "storage_type" : fields[4],
            "update_time" : 0,
            "leases": []
        }

        for i in range(0, (len(fields) - 5) // 3):
            lease_entry = {
                "gateway_address" : fields[5 + i*3],
                "tunnel_id" : int(fields[6 + i*3]),
                "expiration_time" : int(fields[7 + i*3])
            }
            leaseset_dic["leases"].append(lease_entry)

        logger.debug(f"接收到LeaseSet信息，router hash为 {leaseset_dic['hash']}")
        with lock:
            self.mysql_db.add_leaseset(leaseset_dic)

    def consume(self):

        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)  # Poll for messages
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition, continue to next message
                        continue
                    else:
                        # Handle other errors
                        logger.error("Consumer error: {}".format(msg.error()))
                        break

            # Process the message value
                message_value = msg.value().decode('utf-8')  # Decode message bytes to string

                # Split the message value into individual fields

                fields = message_value.split("[|]")
                if fields[0] == "Routerinfo":
                    self._handle_routerinfo(fields)
                elif fields[0] == "LeaseSets":
                    self._handle_leasesets(fields)
                else:
                    continue


        except KeyboardInterrupt:
            pass

        finally:
            self.consumer.close()



# Routerinfo
# \x1c\x20\xd7\x1d\xa5\xa1\x39\x42\xe4\x08\x05\x48\x21\x43\x2c\x7b\x52\x8f\xad\xff\xef\x63\x53\x98\xf1\x66\x2b\x28\x52\xb9\x11\x24\x9d\xe7\x85\xbe\x00\x2a\x86\x72\x49\x6a\x04\xc7\x30\x02\x60\x82\xd9\xfc\xf6\xcb\xb2\xaa\x76\xac\xe2\xdd\xd7\x46\xf4\xe2\xf2\x09\x9d\xe7\x85\xbe\x00\x2a\x86\x72\x49\x6a\x04\xc7\x30\x02\x60\x82\xd9\xfc\xf6\xcb\xb2\xaa\x76\xac\xe2\xdd\xd7\x46\xf4\xe2\xf2\x09\x9d\xe7\x85\xbe\x00\x2a\x86\x72\x49\x6a\x04\xc7\x30\x02\x60\x82\xd9\xfc\xf6\xcb\xb2\xaa\x76\xac\xe2\xdd\xd7\x46\xf4\xe2\xf2\x09\x9d\xe7\x85\xbe\x00\x2a\x86\x72\x49\x6a\x04\xc7\x30\x02\x60\x82\xd9\xfc\xf6\xcb\xb2\xaa\x76\xac\xe2\xdd\xd7\x46\xf4\xe2\xf2\x09\x9d\xe7\x85\xbe\x00\x2a\x86\x72\x49\x6a\x04\xc7\x30\x02\x60\x82\xd9\xfc\xf6\xcb\xb2\xaa\x76\xac\xe2\xdd\xd7\x46\xf4\xe2\xf2\x09\x9d\xe7\x85\xbe\x00\x2a\x86\x72\x49\x6a\x04\xc7\x30\x02\x60\x82\xd9\xfc\xf6\xcb\xb2\xaa\x76\xac\xe2\xdd\xd7\x46\xf4\xe2\xf2\x09\x9d\xe7\x85\xbe\x00\x2a\x86\x72\x49\x6a\x04\xc7\x30\x02\x60\x82\xd9\xfc\xf6\xcb\xb2\xaa\x76\xac\xe2\xdd\xd7\x46\xf4\xe2\xf2\x09
# 1
# RPN
# 9.59
# 2
# 1709899730888
# ECIES_X25519_AEAD
# EDDSA_SHA512_ED25519
# \x4b\xdf\x43\x8f\x7f\x30\xe3\x0a\xcf\x0d\x9e\x54\x88\xd8\x88\x24\xd5\xad\x17\x20\x31\xe0\x43\x32\xee\xf7\x9d\x59\x4e\x79\x41\x1b\x05\x00\x04\x00\x00\x00\x00\x00\x98\x25\xb6\xe0\xc1\x41\x1f\xdf\x40\xcd\x02\x4f\x71\xed\x18\x86\x0f\x7e\xd1\xa5\x73\x5b\xa6\xe2\xc2\x44\xf3\x93\x34\xf5\x63\x99\xa0\x0d\x6e\x66\xe8\x55\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x51\x00\x00\x00\x00\x00\x00\x00\x60\x8a\x72\x66\xe8\x55\x00\x00\x98\x25\xb6\xe0\xc1\x41\x1f\xdf\x40\xcd\x02\x4f\x71\xed\x18\x86\x0f\x7e\xd1\xa5\x73\x5b\xa6\xe2\xc2\x44\xf3\x93\x34\xf5\x63\x99\xb0\x05\x6e\x66\xe8\x55\x00\x00\xa0\x05\x6e\x66\xe8\x55\x00\x00\x98\x25\xb6\xe0\xc1\x41\x1f\xdf\x00\x00\x00\x00\x00\x00\x00\x00\xa1\x00\x00\x00\x00\x00\x00\x00\x3f\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
# 73.53.99.121
# 18026
# FsYEqV8qantJZc96IRo2CETlC3eEj~FZjQwqBC3DchU=
# AUdGUI428hw4JBLMNnV4zA
 
# 0
# 73.53.99.121
# 18026
 
# 0

# LeaseSets
# 8dZJUu13Dt7Tf4dfa4aerqkMiDekzn5EEMAHqADDFSM=
# ELGAMAL
# 1709958296000
# STANDARD_LEASESET2
# cLKxGmb2eFvz8wz4VjTgbpeX5J5fi329j~bYJ2GHD2w=
# 1499365582
# 1709958069000
# Hjxr-BB7Nz0oVDht50seI~igqqva5FB6~yhrs1w-deY=
# 4154923877
# 1709958296000
