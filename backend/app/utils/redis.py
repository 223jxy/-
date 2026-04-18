import redis
import json
import time
from typing import Any, Optional, Callable
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建Redis连接池
redis_pool = redis.ConnectionPool(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', '6379')),
    db=int(os.getenv('REDIS_DB', '0')),
    decode_responses=True,
    max_connections=50
)

# 创建Redis客户端
redis_client = redis.Redis(connection_pool=redis_pool)

# 缓存过期时间配置（秒）
CACHE_EXPIRE = {
    'user': 30 * 60,  # 30分钟
    'book': 15 * 60,  # 15分钟
    'books_list': 5 * 60,  # 5分钟
    'carbon_point': 10 * 60,  # 10分钟
    'stats': 5 * 60,  # 5分钟
    'recommendations': 60 * 60  # 1小时
}


class RedisCache:
    """Redis缓存工具类"""
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    @staticmethod
    def set(key: str, value: Any, expire: int = None) -> bool:
        """设置缓存"""
        try:
            # 自动根据键前缀设置过期时间
            prefix = key.split(':')[0]
            expire_time = expire or CACHE_EXPIRE.get(prefix, 3600)
            redis_client.setex(key, expire_time, json.dumps(value))
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """删除缓存"""
        try:
            redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    @staticmethod
    def delete_pattern(pattern: str) -> int:
        """删除匹配模式的缓存"""
        try:
            keys = redis_client.keys(pattern)
            if keys:
                return redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Redis delete pattern error: {e}")
            return 0
    
    @staticmethod
    def exists(key: str) -> bool:
        """检查缓存是否存在"""
        try:
            return redis_client.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
    
    @staticmethod
    def increment(key: str, amount: int = 1) -> int:
        """递增计数器"""
        try:
            return redis_client.incrby(key, amount)
        except Exception as e:
            print(f"Redis increment error: {e}")
            return 0


# 缓存键前缀
CACHE_PREFIX = {
    'book': 'book:',
    'user': 'user:',
    'carbon_point': 'carbon_point:',
    'books_list': 'books:list:',
    'stats': 'stats:',
    'recommendations': 'recommendations:',
    'order': 'order:',
    'delivery': 'delivery:'
}


# 缓存装饰器
def cache(prefix: str, expire: int = None):
    """缓存装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            key = f"{CACHE_PREFIX[prefix]}{':'.join(map(str, args[1:]))}:{json.dumps(kwargs)}"
            
            # 尝试从缓存获取
            cached_data = RedisCache.get(key)
            if cached_data:
                return cached_data
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            RedisCache.set(key, result, expire)
            
            return result
        return wrapper
    return decorator


# 缓存统计
def cache_stats():
    """获取缓存统计信息"""
    try:
        info = redis_client.info()
        return {
            'connected_clients': info.get('connected_clients', 0),
            'used_memory_mb': info.get('used_memory_rss', 0) / (1024 * 1024),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
            'hit_rate': (info.get('keyspace_hits', 0) / (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1))) * 100
        }
    except Exception as e:
        print(f"Redis stats error: {e}")
        return {}


# 缓存预热
def warmup_cache():
    """缓存预热"""
    print("开始缓存预热...")
    # 这里可以添加预热逻辑
    print("缓存预热完成")