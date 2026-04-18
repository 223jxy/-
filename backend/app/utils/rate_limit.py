import time
from fastapi import HTTPException, Request
from app.utils.redis import RedisCache

# 限流配置
RATE_LIMITS = {
    "default": {"requests": 100, "seconds": 60},  # 每分钟100个请求
    "books": {"requests": 50, "seconds": 60},    # 每分钟50个请求
    "users": {"requests": 30, "seconds": 60},    # 每分钟30个请求
}


async def rate_limit(key_prefix: str = "default"):
    """
    接口限流依赖
    
    - **key_prefix**: 限流配置键
    """
    async def _rate_limit(request: Request):
        # 获取客户端IP
        client_ip = request.client.host
        
        # 生成限流键
        limit_key = f"rate_limit:{key_prefix}:{client_ip}"
        
        # 获取限流配置
        limit_config = RATE_LIMITS.get(key_prefix, RATE_LIMITS["default"])
        max_requests = limit_config["requests"]
        window_seconds = limit_config["seconds"]
        
        # 获取当前请求数
        current_count = RedisCache.get(limit_key) or 0
        
        if current_count >= max_requests:
            raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
        
        # 增加请求计数
        if current_count == 0:
            # 第一次请求，设置过期时间
            RedisCache.set(limit_key, 1, expire=window_seconds)
        else:
            # 后续请求，增加计数
            # 注意：这里简化处理，实际应该使用Redis的INCR命令
            RedisCache.set(limit_key, current_count + 1, expire=window_seconds)
        
        return None
    
    return _rate_limit