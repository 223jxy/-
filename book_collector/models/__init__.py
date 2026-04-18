"""
数据模型模块初始化文件
"""
from .book import (
    BookData,
    CollectionResult,
    UploadResult,
    SellerInfo,
    ConditionLevel,
    StockStatus
)

__all__ = [
    'BookData',
    'CollectionResult',
    'UploadResult',
    'SellerInfo',
    'ConditionLevel',
    'StockStatus'
]