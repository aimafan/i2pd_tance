FROM ubuntu:22.04

# 设置工作目录
WORKDIR /app

# 安装基本工具和依赖
RUN apt-get update && apt-get install -y \
    vim \
    sudo \
    build-essential \
    debhelper \
    libboost-date-time-dev \
    libboost-filesystem-dev \
    libboost-program-options-dev \
    libboost-system-dev \
    libssl-dev \
    zlib1g-dev \
    librdkafka++1 \
    libmysqlcppconn-dev \
    python3.10 \
    python3-pip \
    cmake \
    python3.10-venv \
    librdkafka-dev  \
    telnet  \
    net-tools \
    wget    \
    curl    \
    openjdk-17-jdk

# 添加一个普通用户和sudo权限
# RUN useradd -m user && echo "user:user" | chpasswd && adduser user sudo

RUN update-alternatives --set editor /usr/bin/vim.basic
# 切换到普通用户
# USER user
ADD . .
RUN pip3 install --no-cache-dir -r mycode/requirements.txt

# RUN nohup kafka_2.13-3.7.0/bin/zookeeper-server-start.sh kafka_2.13-3.7.0/config/zookeeper.properties > /dev/null 2>&1 &
# RUN nohup kafka_2.13-3.7.0/bin/kafka-server-start.sh kafka_2.13-3.7.0/config/server.properties > /dev/null 2>&1 &
# RUN nohup kafka_2.13-3.7.0/bin/kafka-topics.sh --create --topic darknet --bootstrap-server localhost:9092 > /dev/null 2>&1 &

RUN cd build; make

# 设置vim为默认编辑器
RUN cd mycode


CMD ["bash"]
