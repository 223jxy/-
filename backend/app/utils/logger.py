# 后端日志工具
from loguru import logger
import os
import json
from datetime import datetime
from typing import Any, Dict, Optional

# 确保日志目录存在
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志格式
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <blue>user_id={extra[user_id]}</blue> | <blue>request_id={extra[request_id]}</blue> | <level>{message}</level>"

# 配置日志文件
logger.add(
    os.path.join(LOG_DIR, "info.log"),
    level="INFO",
    format=LOG_FORMAT,
    rotation="100 MB",
    retention="7 days",
    compression="zip"
)

logger.add(
    os.path.join(LOG_DIR, "error.log"),
    level="ERROR",
    format=LOG_FORMAT,
    rotation="100 MB",
    retention="30 days",
    compression="zip"
)

logger.add(
    os.path.join(LOG_DIR, "debug.log"),
    level="DEBUG",
    format=LOG_FORMAT,
    rotation="100 MB",
    retention="3 days",
    compression="zip"
)

class Logger:
    """日志工具类"""
    
    def __init__(self):
        self.user_id = None
        self.request_id = None
    
    def set_user_id(self, user_id: Optional[int]) -> None:
        """设置用户ID"""
        self.user_id = user_id
    
    def set_request_id(self, request_id: Optional[str]) -> None:
        """设置请求ID"""
        self.request_id = request_id
    
    def _get_extra(self) -> Dict[str, Any]:
        """获取额外信息"""
        return {
            "user_id": self.user_id or "unknown",
            "request_id": self.request_id or "unknown"
        }
    
    def debug(self, message: str, **kwargs) -> None:
        """调试日志"""
        logger.debug(message, extra=self._get_extra(), **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """信息日志"""
        logger.info(message, extra=self._get_extra(), **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """警告日志"""
        logger.warning(message, extra=self._get_extra(), **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """错误日志"""
        logger.error(message, extra=self._get_extra(), **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """致命错误日志"""
        logger.critical(message, extra=self._get_extra(), **kwargs)
    
    def operation(self, operation: str, **kwargs) -> None:
        """操作日志"""
        self.info(f"Operation: {operation}", operation=operation, **kwargs)
    
    def api_request(self, url: str, method: str, **kwargs) -> None:
        """API请求日志"""
        self.info(f"API Request: {method} {url}", url=url, method=method, **kwargs)
    
    def api_response(self, url: str, method: str, status_code: int, duration: float, **kwargs) -> None:
        """API响应日志"""
        if status_code >= 400:
            self.error(f"API Response: {method} {url} {status_code}", 
                     url=url, method=method, status_code=status_code, duration=duration, **kwargs)
        else:
            self.info(f"API Response: {method} {url} {status_code}", 
                     url=url, method=method, status_code=status_code, duration=duration, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """异常日志"""
        logger.exception(message, extra=self._get_extra(), **kwargs)
    
    def business(self, event: str, **kwargs) -> None:
        """业务日志"""
        self.info(f"Business Event: {event}", event=event, **kwargs)
    
    def audit(self, action: str, **kwargs) -> None:
        """审计日志"""
        self.info(f"Audit Action: {action}", action=action, **kwargs)
    
    def performance(self, metric: str, value: float, **kwargs) -> None:
        """性能日志"""
        self.info(f"Performance Metric: {metric} = {value}", metric=metric, value=value, **kwargs)

# 导出单例
logger_instance = Logger()

# 中间件：添加请求ID和用户ID到日志
async def log_request_middleware(request, call_next):
    """请求日志中间件"""
    import uuid
    from fastapi import Request
    from jose import JWTError, jwt
    import os
    from dotenv import load_dotenv
    
    # 加载环境变量
    load_dotenv()
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM = "HS256"
    
    # 生成请求ID
    request_id = str(uuid.uuid4())
    
    # 从请求中获取用户ID
    user_id = None
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                # 这里可以从数据库中查询用户ID
                # 为了简化，暂时使用username作为标识
                user_id = username
        except JWTError:
            pass
    
    # 设置日志的请求ID和用户ID
    logger_instance.set_request_id(request_id)
    logger_instance.set_user_id(user_id)
    
    # 记录请求开始
    logger_instance.info(f"Request Start: {request.method} {request.url.path}", 
                       method=request.method, path=request.url.path, 
                       client_ip=request.client.host)
    
    # 处理请求
    response = await call_next(request)
    
    # 记录请求结束
    logger_instance.info(f"Request End: {request.method} {request.url.path} {response.status_code}", 
                       method=request.method, path=request.url.path, 
                       status_code=response.status_code, client_ip=request.client.host)
    
    return response