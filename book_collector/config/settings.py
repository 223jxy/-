"""
系统配置文件
"""
import os
from typing import List
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = Path(__file__).resolve().parent

# 数据库配置
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'book_collector'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'pool_size': 10,
    'max_overflow': 20
}

# Redis配置
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 0)),
    'password': os.getenv('REDIS_PASSWORD', None),
    'max_connections': 50
}

# 图片存储配置
IMAGE_STORAGE = {
    'base_path': os.path.join(BASE_DIR, 'data', 'images'),
    'max_size': 5 * 1024 * 1024,  # 5MB
    'allowed_formats': ['jpg', 'jpeg', 'png', 'webp'],
    'quality': 85,
    'thumbnail_size': (200, 300)
}

# 采集配置
COLLECTION_CONFIG = {
    'batch_size': 50,  # 每次采集的数量
    'max_retries': 3,  # 最大重试次数
    'timeout': 30,  # 请求超时时间（秒）
    'delay_between_requests': 2,  # 请求间隔（秒）
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'concurrent_requests': 5  # 并发请求数
}

# 定时任务配置
SCHEDULER_CONFIG = {
    'enabled': True,
    'collection_interval': 3600,  # 采集间隔（秒），默认1小时
    'update_interval': 86400,  # 更新间隔（秒），默认24小时
    'cleanup_interval': 604800,  # 清理间隔（秒），默认7天
    'cleanup_days': 30  # 保留天数
}

# 数据校验配置
VALIDATION_CONFIG = {
    'min_price': 0.01,  # 最低价格
    'max_price': 10000,  # 最高价格
    'min_title_length': 2,  # 最小标题长度
    'max_title_length': 200,  # 最大标题长度
    'required_fields': ['title', 'original_price', 'secondhand_price', 'platform'],
    'isbn_pattern': r'^\d{10}(\d{3})?$',  # ISBN正则表达式
    'price_ratio_range': (0.01, 2.0)  # 二手价与原价比例范围
}

# 日志配置
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': os.path.join(BASE_DIR, 'logs', 'collector.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': os.path.join(BASE_DIR, 'logs', 'error.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# 数据上传配置
UPLOAD_CONFIG = {
    'batch_size': 100,  # 批量上传数量
    'max_retries': 5,  # 最大重试次数
    'timeout': 60,  # 上传超时时间（秒）
    'api_endpoint': os.getenv('UPLOAD_API_ENDPOINT', 'http://localhost:8000/api/books'),
    'api_key': os.getenv('UPLOAD_API_KEY', ''),
    'compression': True  # 是否启用压缩
}

# 性能监控配置
MONITORING_CONFIG = {
    'enabled': True,
    'metrics_port': 9090,
    'alert_threshold': {
        'error_rate': 0.05,  # 错误率阈值（5%）
        'response_time': 5.0,  # 响应时间阈值（秒）
        'memory_usage': 0.8  # 内存使用阈值（80%）
    }
}

# 安全配置
SECURITY_CONFIG = {
    'enable_rate_limiting': True,
    'rate_limit': 100,  # 每分钟请求数
    'enable_proxy': False,
    'proxy_list': [],
    'verify_ssl': True,
    'max_request_size': 10485760  # 10MB
}

# 开发环境配置
if os.getenv('ENVIRONMENT') == 'development':
    LOGGING_CONFIG['handlers']['console']['level'] = 'DEBUG'
    COLLECTION_CONFIG['delay_between_requests'] = 1
    MONITORING_CONFIG['enabled'] = False