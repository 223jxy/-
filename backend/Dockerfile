# 后端Dockerfile

# 基础镜像
FROM python:3.13-slim as builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt
COPY requirements.txt ./

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 生产环境镜像
FROM python:3.13-slim

# 添加非root用户
RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制源代码
COPY . .

# 创建日志目录
RUN mkdir -p logs && \
    chown -R appuser:appgroup logs && \
    chmod -R 755 logs

# 暴露端口
EXPOSE 8000

# 切换到非root用户
USER appuser

# 启动应用
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000", "--timeout", "300", "--access-logfile", "logs/access.log", "--error-logfile", "logs/error.log", "--max-requests", "10000", "--max-requests-jitter", "5000", "--keep-alive", "20"]