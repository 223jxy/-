from fastapi import Request, HTTPException
from datetime import datetime, timedelta
import hashlib
import json
from app.utils.redis import redis_client

# 防重放攻击中间件
async def replay_protection_middleware(request: Request, call_next):
    # 跳过GET请求，因为GET请求通常是幂等的
    if request.method == "GET":
        return await call_next(request)
    
    # 获取请求体
    try:
        body = await request.body()
        # 解析请求体
        try:
            body_json = json.loads(body.decode())
        except json.JSONDecodeError:
            body_json = {}
    except Exception:
        body_json = {}
    
    # 获取请求头中的时间戳和nonce
    timestamp = request.headers.get("X-Timestamp")
    nonce = request.headers.get("X-Nonce")
    
    # 验证时间戳和nonce是否存在
    if not timestamp or not nonce:
        raise HTTPException(status_code=400, detail="Missing required headers: X-Timestamp or X-Nonce")
    
    # 验证时间戳是否在有效范围内（10分钟）
    try:
        request_time = datetime.fromtimestamp(int(timestamp))
        current_time = datetime.now()
        if abs((current_time - request_time).total_seconds()) > 600:
            raise HTTPException(status_code=400, detail="Invalid timestamp")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format")
    
    # 生成请求的唯一标识符
    request_id = hashlib.sha256(f"{timestamp}:{nonce}:{request.method}:{request.url.path}:{json.dumps(body_json, sort_keys=True)}".encode()).hexdigest()
    
    # 检查请求是否已经被处理过
    if redis_client.exists(f"replay:{request_id}"):
        raise HTTPException(status_code=400, detail="Replay attack detected")
    
    # 存储请求标识符，设置过期时间为10分钟
    redis_client.setex(f"replay:{request_id}", 600, "1")
    
    # 继续处理请求
    response = await call_next(request)
    return response