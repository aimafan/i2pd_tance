#/bin/bash

nohup kafka_2.13-3.7.0/bin/zookeeper-server-start.sh kafka_2.13-3.7.0/config/zookeeper.properties > /dev/null 2>&1 &
sleep 5
nohup kafka_2.13-3.7.0/bin/kafka-server-start.sh kafka_2.13-3.7.0/config/server.properties > /dev/null 2>&1 &
sleep 5
nohup kafka_2.13-3.7.0/bin/kafka-topics.sh --create --topic darkneti2p --bootstrap-server localhost:9092 > /dev/null 2>&1 &

sleep 5

python3 mycode/main.py