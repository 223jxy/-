#!/bin/bash

# 后端部署脚本

set -e

echo "===== 书驿云桥后端部署脚本 ====="

# 检查Python版本
echo "检查Python版本..."
python3 --version

# 选择环境
if [ -z "$ENVIRONMENT" ]; then
  ENVIRONMENT="production"
fi

echo "部署环境: $ENVIRONMENT"

# 创建虚拟环境
if [ ! -d "venv" ]; then
  echo "创建虚拟环境..."
  python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 确保日志目录存在
mkdir -p logs

# 配置环境变量
echo "配置环境变量..."
export ENVIRONMENT="$ENVIRONMENT"

# 启动应用
echo "启动应用..."

# 使用Gunicorn+Uvicorn启动
if [ "$1" == "start" ]; then
  echo "使用Gunicorn启动应用..."
  # 根据环境选择配置文件
  if [ "$ENVIRONMENT" == "production" ]; then
    export ENV_FILE=".env.production"
  elif [ "$ENVIRONMENT" == "testing" ]; then
    export ENV_FILE=".env.testing"
  else
    export ENV_FILE=".env.development"
  fi
  
  echo "使用配置文件: $ENV_FILE"
  
  # 启动Gunicorn
  gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app \
    --bind 0.0.0.0:8000 \
    --timeout 300 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --daemon \
    --worker-class uvicorn.workers.UvicornWorker \
    --max-requests 10000 \
    --max-requests-jitter 5000 \
    --keep-alive 20
  
  echo "应用已启动"

# 停止应用
elif [ "$1" == "stop" ]; then
  echo "停止应用..."
  pkill -f gunicorn || true
  echo "应用已停止"

# 重启应用
elif [ "$1" == "restart" ]; then
  echo "重启应用..."
  pkill -f gunicorn || true
  sleep 2
  
  # 根据环境选择配置文件
  if [ "$ENVIRONMENT" == "production" ]; then
    export ENV_FILE=".env.production"
  elif [ "$ENVIRONMENT" == "testing" ]; then
    export ENV_FILE=".env.testing"
  else
    export ENV_FILE=".env.development"
  fi
  
  echo "使用配置文件: $ENV_FILE"
  
  # 启动Gunicorn
  gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app \
    --bind 0.0.0.0:8000 \
    --timeout 300 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --daemon \
    --worker-class uvicorn.workers.UvicornWorker \
    --max-requests 10000 \
    --max-requests-jitter 5000 \
    --keep-alive 20
  
  echo "应用已重启"

# 查看状态
elif [ "$1" == "status" ]; then
  echo "查看应用状态..."
  ps aux | grep gunicorn | grep -v grep

# 部署
elif [ "$1" == "deploy" ]; then
  echo "部署应用..."
  
  # 停止旧应用
  pkill -f gunicorn || true
  sleep 2
  
  # 安装依赖
  echo "安装依赖..."
  pip install -r requirements.txt
  
  # 根据环境选择配置文件
  if [ "$ENVIRONMENT" == "production" ]; then
    export ENV_FILE=".env.production"
  elif [ "$ENVIRONMENT" == "testing" ]; then
    export ENV_FILE=".env.testing"
  else
    export ENV_FILE=".env.development"
  fi
  
  echo "使用配置文件: $ENV_FILE"
  
  # 启动新应用
  gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app \
    --bind 0.0.0.0:8000 \
    --timeout 300 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --daemon \
    --worker-class uvicorn.workers.UvicornWorker \
    --max-requests 10000 \
    --max-requests-jitter 5000 \
    --keep-alive 20
  
  echo "应用已部署"

# 查看日志
elif [ "$1" == "logs" ]; then
  echo "查看应用日志..."
  tail -f logs/access.log logs/error.log

# 清理日志
elif [ "$1" == "clean" ]; then
  echo "清理日志..."
  find logs -name "*.log" -type f -exec truncate -s 0 {} \;
  echo "日志已清理"

else
  echo "用法: ./deploy.sh [start|stop|restart|status|deploy|logs|clean]"
  exit 1
fi

# 显示部署信息
echo "\n部署信息："
echo "- 部署环境: $ENVIRONMENT"
echo "- 部署时间: $(date)"
echo "- Python版本: $(python3 --version)"
echo "- 虚拟环境: $(which python)"

echo "===== 部署脚本执行完成 ====="