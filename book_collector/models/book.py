"""
书籍数据模型
定义二手书数据结构
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum

class ConditionLevel(str, Enum):
    """成色等级"""
    BRAND_NEW = "全新"
    LIKE_NEW = "九成新"
    GOOD = "八成新"
    FAIR = "七成新"
    POOR = "六成新及以下"

class StockStatus(str, Enum):
    """库存状态"""
    AVAILABLE = "在售"
    SOLD = "已售"
    RESERVED = "已预订"
    OFF_SHELF = "下架"

class SellerInfo(BaseModel):
    """卖家信息"""
    name: str = Field(..., description="卖家名称")
    rating: Optional[float] = Field(None, ge=0, le=5, description="卖家评分")
    sales_count: Optional[int] = Field(None, ge=0, description="销售数量")
    location: Optional[str] = Field(None, description="所在地")
    response_rate: Optional[float] = Field(None, ge=0, le=100, description="响应率")

class BookData(BaseModel):
    """书籍数据模型"""
    book_id: str = Field(..., description="书籍唯一标识")
    title: str = Field(..., min_length=2, max_length=200, description="书名")
    author: Optional[str] = Field(None, max_length=100, description="作者")
    publisher: Optional[str] = Field(None, max_length=100, description="出版社")
    publish_date: Optional[str] = Field(None, description="出版日期")
    isbn: Optional[str] = Field(None, description="ISBN编号")
    original_price: float = Field(..., gt=0, description="原价")
    secondhand_price: float = Field(..., gt=0, description="二手售价")
    condition: str = Field(..., description="成色描述")
    condition_score: Optional[int] = Field(None, ge=1, le=10, description="成色评分（1-10）")
    seller_info: Optional[SellerInfo] = Field(None, description="卖家信息")
    platform: str = Field(..., description="来源平台")
    platform_url: str = Field(..., description="平台链接")
    cover_image: Optional[str] = Field(None, description="封面图片路径")
    description: Optional[str] = Field(None, max_length=2000, description="书籍描述")
    tags: List[str] = Field(default_factory=list, description="标签")
    category: Optional[str] = Field(None, max_length=50, description="分类")
    stock_status: Optional[StockStatus] = Field(None, description="库存状态")
    collected_at: datetime = Field(default_factory=datetime.now, description="采集时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    @validator('secondhand_price')
    def validate_price_ratio(cls, v, values):
        """验证二手价与原价的合理比例"""
        if 'original_price' in values:
            original_price = values['original_price']
            if original_price > 0:
                ratio = v / original_price
                if not (0.01 <= ratio <= 2.0):
                    raise ValueError(f'二手价与原价比例异常: {ratio:.2f}')
        return v
    
    @validator('isbn')
    def validate_isbn(cls, v):
        """验证ISBN格式"""
        if v:
            import re
            if not re.match(r'^\d{10}(\d{3})?$', v):
                raise ValueError(f'ISBN格式不正确: {v}')
        return v
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return self.dict()
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return self.json()

class CollectionResult(BaseModel):
    """采集结果"""
    success: bool = Field(..., description="是否成功")
    platform: str = Field(..., description="平台名称")
    total_collected: int = Field(default=0, description="采集总数")
    valid_count: int = Field(default=0, description="有效数量")
    invalid_count: int = Field(default=0, description="无效数量")
    error_count: int = Field(default=0, description="错误数量")
    books: List[BookData] = Field(default_factory=list, description="书籍数据列表")
    errors: List[str] = Field(default_factory=list, description="错误信息列表")
    start_time: datetime = Field(default_factory=datetime.now, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    
    @property
    def duration(self) -> Optional[float]:
        """采集耗时（秒）"""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_collected > 0:
            return (self.valid_count / self.total_collected) * 100
        return 0.0

class UploadResult(BaseModel):
    """上传结果"""
    success: bool = Field(..., description="是否成功")
    total_uploaded: int = Field(default=0, description="上传总数")
    success_count: int = Field(default=0, description="成功数量")
    failed_count: int = Field(default=0, description="失败数量")
    batch_id: Optional[str] = Field(None, description="批次ID")
    errors: List[str] = Field(default_factory=list, description="错误信息列表")
    start_time: datetime = Field(default_factory=datetime.now, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    
    @property
    def duration(self) -> Optional[float]:
        """上传耗时（秒）"""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None