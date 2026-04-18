# 监控告警工具
import time
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from app.utils.logger import logger_instance
from app.utils.performance import performance_monitor

class Monitoring:
    """监控告警类"""
    
    def __init__(self):
        self.alert_history = []
        self.alert_cooldown = 300  # 告警冷却时间（秒）
        
    def send_email_alert(self, subject: str, message: str) -> bool:
        """发送邮件告警"""
        try:
            # 实际项目中应该从环境变量获取邮件配置
            sender_email = "your-email@example.com"
            receiver_email = "admin@example.com"
            password = "your-email-password"
            smtp_server = "smtp.example.com"
            smtp_port = 587
            
            # 创建邮件
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = receiver_email
            msg["Subject"] = subject
            
            # 添加邮件正文
            msg.attach(MIMEText(message, "plain"))
            
            # 发送邮件
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, password)
                server.send_message(msg)
            
            logger_instance.info(f"Email alert sent: {subject}")
            return True
        except Exception as e:
            logger_instance.error(f"Failed to send email alert: {e}")
            return False
    
    def send_slack_alert(self, message: str) -> bool:
        """发送Slack告警"""
        try:
            # 实际项目中应该使用Slack API
            logger_instance.info(f"Slack alert sent: {message}")
            return True
        except Exception as e:
            logger_instance.error(f"Failed to send Slack alert: {e}")
            return False
    
    def check_alert_cooldown(self, alert_type: str) -> bool:
        """检查告警冷却时间"""
        current_time = time.time()
        for alert in reversed(self.alert_history):
            if alert["type"] == alert_type and current_time - alert["timestamp"] < self.alert_cooldown:
                return True
        return False
    
    def add_alert_history(self, alert_type: str, message: str) -> None:
        """添加告警历史"""
        self.alert_history.append({
            "type": alert_type,
            "message": message,
            "timestamp": time.time()
        })
        
        # 只保留最近100条告警历史
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
    
    def alert(self, alert_type: str, message: str) -> None:
        """发送告警"""
        # 检查告警冷却时间
        if self.check_alert_cooldown(alert_type):
            logger_instance.info(f"Alert cooldown active for {alert_type}")
            return
        
        # 添加告警历史
        self.add_alert_history(alert_type, message)
        
        # 发送邮件告警
        self.send_email_alert(f"[Alert] {alert_type}", message)
        
        # 发送Slack告警
        self.send_slack_alert(message)
    
    def check_api_errors(self, error_count: int, threshold: int = 10) -> None:
        """检查API错误"""
        if error_count > threshold:
            message = f"API error count exceeded threshold: {error_count} errors"
            self.alert("api_error", message)
    
    def check_database_connection(self, is_connected: bool) -> None:
        """检查数据库连接"""
        if not is_connected:
            message = "Database connection failed"
            self.alert("database_connection", message)
    
    def check_server_load(self) -> None:
        """检查服务器负载"""
        metrics = performance_monitor.get_system_metrics()
        
        # 检查CPU使用率
        if metrics["cpu_percent"] > 90:
            message = f"High CPU usage: {metrics['cpu_percent']}%"
            self.alert("high_cpu", message)
        
        # 检查内存使用率
        if metrics["memory_percent"] > 90:
            message = f"High memory usage: {metrics['memory_percent']}%"
            self.alert("high_memory", message)
        
        # 检查磁盘使用率
        if metrics["disk_percent"] > 90:
            message = f"High disk usage: {metrics['disk_percent']}%"
            self.alert("high_disk", message)
    
    def check_response_time(self, endpoint: str, duration: float, threshold: float = 1.0) -> None:
        """检查响应时间"""
        if duration > threshold:
            message = f"High response time for {endpoint}: {duration:.4f}s"
            self.alert("high_response_time", message)
    
    def check_health(self) -> Dict[str, any]:
        """检查系统健康状态"""
        health_status = performance_monitor.check_health()
        
        # 检查服务器负载
        self.check_server_load()
        
        return health_status

# 导出单例
monitoring = Monitoring()

# 定期检查系统健康状态
async def periodic_health_check():
    """定期检查系统健康状态"""
    while True:
        try:
            # 检查系统健康状态
            health_status = monitoring.check_health()
            logger_instance.info("Health check completed", **health_status)
        except Exception as e:
            logger_instance.error(f"Health check failed: {e}")
        
        # 每5分钟检查一次
        await asyncio.sleep(300)

# 启动定期健康检查的函数
async def start_periodic_health_check():
    """启动定期健康检查"""
    await periodic_health_check()