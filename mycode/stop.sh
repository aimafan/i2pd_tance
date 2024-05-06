#!/bin/bash

# 获取包含 "i2pd" 的进程号列表
pids=$(pgrep -f "i2pd")

if [ -z "$pids" ]; then
  echo ""
else
  echo "找到以下包含 'i2pd' 的进程：$pids"
# 使用kill -9终止进程
echo "终止进程..."
sudo kill -9 $pids
echo "进程已终止。"

fi