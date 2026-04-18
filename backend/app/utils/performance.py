# 后端性能监控工具
import time
import psutil
import os
from typing import Dict, Any, Optional
from app.utils.logger import logger_instance
from opentelemetry import trace
from opentelemetry.trace import SpanKind

# 获取tracer
tracer = trace.get_tracer(__name__)

class PerformanceMonitor:
    """性能监控工具类"""
    
    def __init__(self):
        self.start_times = {}
    
    def start_timer(self, key: str) -> None:
        """开始计时"""
        self.start_times[key] = time.time()
    
    def end_timer(self, key: str) -> float:
        """结束计时并返回耗时"""
        if key in self.start_times:
            duration = time.time() - self.start_times[key]
            del self.start_times[key]
            return duration
        return 0.0
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "network_sent": psutil.net_io_counters().bytes_sent,
            "network_recv": psutil.net_io_counters().bytes_recv,
            "process_memory": psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024,  # MB
            "process_cpu": psutil.Process(os.getpid()).cpu_percent()
        }
        return metrics
    
    def monitor_function(self, func):
        """装饰器：监控函数执行性能"""
        def wrapper(*args, **kwargs):
            function_name = func.__name__
            logger_instance.info(f"Function start: {function_name}")
            
            # 开始计时
            self.start_timer(function_name)
            
            # 创建span
            with tracer.start_as_current_span(function_name, kind=SpanKind.INTERNAL) as span:
                try:
                    # 执行函数
                    result = func(*args, **kwargs)
                    # 结束计时
                    duration = self.end_timer(function_name)
                    # 记录函数执行时间
                    logger_instance.info(f"Function end: {function_name} - {duration:.4f}s", 
                                       function=function_name, duration=duration)
                    # 添加span属性
                    span.set_attribute("function.duration", duration)
                    span.set_attribute("function.result", str(result))
                    return result
                except Exception as e:
                    # 结束计时
                    duration = self.end_timer(function_name)
                    # 记录异常
                    logger_instance.error(f"Function error: {function_name} - {e}", 
                                        function=function_name, duration=duration, error=str(e))
                    # 添加span属性
                    span.set_attribute("function.duration", duration)
                    span.set_attribute("function.error", str(e))
                    span.record_exception(e)
                    raise
        return wrapper
    
    def monitor_api(self, endpoint: str):
        """装饰器：监控API端点性能"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                logger_instance.info(f"API start: {endpoint}")
                
                # 开始计时
                self.start_timer(endpoint)
                
                # 创建span
                with tracer.start_as_current_span(endpoint, kind=SpanKind.SERVER) as span:
                    try:
                        # 执行API函数
                        result = func(*args, **kwargs)
                        # 结束计时
                        duration = self.end_timer(endpoint)
                        # 记录API执行时间
                        logger_instance.info(f"API end: {endpoint} - {duration:.4f}s", 
                                           endpoint=endpoint, duration=duration)
                        # 添加span属性
                        span.set_attribute("api.endpoint", endpoint)
                        span.set_attribute("api.duration", duration)
                        return result
                    except Exception as e:
                        # 结束计时
                        duration = self.end_timer(endpoint)
                        # 记录异常
                        logger_instance.error(f"API error: {endpoint} - {e}", 
                                            endpoint=endpoint, duration=duration, error=str(e))
                        # 添加span属性
                        span.set_attribute("api.endpoint", endpoint)
                        span.set_attribute("api.duration", duration)
                        span.set_attribute("api.error", str(e))
                        span.record_exception(e)
                        raise
            return wrapper
        return decorator
    
    def log_system_metrics(self) -> None:
        """记录系统指标"""
        metrics = self.get_system_metrics()
        logger_instance.info("System metrics", **metrics)
    
    def check_health(self) -> Dict[str, Any]:
        """检查系统健康状态"""
        metrics = self.get_system_metrics()
        health_status = "healthy"
        
        # 检查系统指标是否正常
        if metrics["cpu_percent"] > 90:
            health_status = "warning: high CPU usage"
        if metrics["memory_percent"] > 90:
            health_status = "warning: high memory usage"
        if metrics["disk_percent"] > 90:
            health_status = "warning: high disk usage"
        
        return {
            "status": health_status,
            "metrics": metrics
        }

# 导出单例
performance_monitor = PerformanceMonitor()

# 中间件：监控请求性能
async def performance_middleware(request, call_next):
    """请求性能监控中间件"""
    # 开始计时
    start_time = time.time()
    
    # 处理请求
    response = await call_next(request)
    
    # 结束计时
    duration = time.time() - start_time
    
    # 记录请求性能
    logger_instance.info(f"Request performance: {request.method} {request.url.path} - {duration:.4f}s", 
                       method=request.method, path=request.url.path, duration=duration, 
                       status_code=response.status_code)
    
    # 记录系统指标
    if duration > 1.0:  # 只在请求耗时超过1秒时记录系统指标
        performance_monitor.log_system_metrics()
    
    return response