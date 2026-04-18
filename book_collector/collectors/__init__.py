"""
采集器模块初始化文件
"""
from .base import BaseCollector
from .kongfuzi import KongfuziCollector
from .duozhuayu import DuozhuayuCollector
from .xianyu import XianyuCollector

__all__ = [
    'BaseCollector',
    'KongfuziCollector',
    'DuozhuayuCollector',
    'XianyuCollector'
]