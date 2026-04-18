import time
from functools import wraps
from app.utils.redis import RedisCache

# 熔断配置
CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 5,  # 失败阈值
    "recovery_timeout": 30,  # 恢复超时时间（秒）
    "timeout": 5,  # 超时时间（秒）
}


class CircuitBreaker:
    """电路熔断类"""
    
    def __init__(self, key: str, failure_threshold: int = None, recovery_timeout: int = None, timeout: int = None):
        self.key = key
        self.failure_threshold = failure_threshold or CIRCUIT_BREAKER_CONFIG["failure_threshold"]
        self.recovery_timeout = recovery_timeout or CIRCUIT_BREAKER_CONFIG["recovery_timeout"]
        self.timeout = timeout or CIRCUIT_BREAKER_CONFIG["timeout"]
    
    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 检查熔断状态
            state = RedisCache.get(f"circuit_breaker:{self.key}:state")
            last_failure_time = RedisCache.get(f"circuit_breaker:{self.key}:last_failure")
            failure_count = RedisCache.get(f"circuit_breaker:{self.key}:failure_count") or 0
            
            # 如果处于熔断状态，检查是否可以恢复
            if state == "OPEN":
                if last_failure_time and (time.time() - last_failure_time) > self.recovery_timeout:
                    # 尝试恢复，设置为半开状态
                    RedisCache.set(f"circuit_breaker:{self.key}:state", "HALF_OPEN")
                else:
                    # 仍然处于熔断状态，拒绝请求
                    from fastapi import HTTPException
                    raise HTTPException(status_code=503, detail="服务暂时不可用，请稍后再试")
            
            try:
                # 执行函数
                result = await func(*args, **kwargs)
                
                # 成功执行，重置熔断状态
                RedisCache.delete(f"circuit_breaker:{self.key}:failure_count")
                RedisCache.set(f"circuit_breaker:{self.key}:state", "CLOSED")
                
                return result
            except Exception as e:
                # 执行失败，增加失败计数
                failure_count += 1
                RedisCache.set(f"circuit_breaker:{self.key}:failure_count", failure_count)
                RedisCache.set(f"circuit_breaker:{self.key}:last_failure", time.time())
                
                # 检查是否达到失败阈值
                if failure_count >= self.failure_threshold:
                    RedisCache.set(f"circuit_breaker:{self.key}:state", "OPEN")
                
                # 重新抛出异常
                raise
        
        return wrapper