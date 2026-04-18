"""
平台配置文件
定义各个二手书交易平台的配置信息
"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class PlatformConfig:
    """平台配置数据类"""
    name: str
    base_url: str
    search_url: str
    detail_url_pattern: str
    image_url_pattern: str
    selectors: Dict[str, str]
    rate_limit: int
    enabled: bool
    requires_auth: bool = False

# 平台配置列表
PLATFORMS: Dict[str, PlatformConfig] = {
    'kongfuzi': PlatformConfig(
        name='孔夫子旧书网',
        base_url='https://www.kongfz.com',
        search_url='https://search.kongfz.com/product/result/',
        detail_url_pattern='https://www.kongfz.com/item/{id}',
        image_url_pattern='https://www.kongfz.com{path}',
        selectors={
            'book_list': '.item-list .item',
            'title': '.item-title a',
            'price': '.item-price',
            'original_price': '.item-original-price',
            'condition': '.item-condition',
            'seller': '.seller-name',
            'seller_rating': '.seller-rating',
            'image': '.item-cover img',
            'detail_link': '.item-title a',
            'isbn': '.item-isbn',
            'publisher': '.item-publisher',
            'publish_date': '.item-publish-date'
        },
        rate_limit=10,
        enabled=True,
        requires_auth=False
    ),
    'duozhuayu': PlatformConfig(
        name='多抓鱼',
        base_url='https://www.duozhuayu.com',
        search_url='https://www.duozhuayu.com/search',
        detail_url_pattern='https://www.duozhuayu.com/book/{id}',
        image_url_pattern='https://www.duozhuayu.com{path}',
        selectors={
            'book_list': '.book-list .book-item',
            'title': '.book-title',
            'price': '.book-price',
            'original_price': '.book-original-price',
            'condition': '.book-condition',
            'seller': '.seller-info .name',
            'seller_rating': '.seller-info .rating',
            'image': '.book-cover img',
            'detail_link': '.book-title a',
            'isbn': '.book-info .isbn',
            'publisher': '.book-info .publisher',
            'publish_date': '.book-info .date'
        },
        rate_limit=15,
        enabled=True,
        requires_auth=False
    ),
    'xianyu': PlatformConfig(
        name='闲鱼',
        base_url='https://www.goofish.com',
        search_url='https://www.goofish.com/search',
        detail_url_pattern='https://www.goofish.com/item/{id}',
        image_url_pattern='https://www.goofish.com{path}',
        selectors={
            'book_list': '.search-item-wrapper .search-item',
            'title': '.search-item-title',
            'price': '.price',
            'original_price': '.price-original',
            'condition': '.condition',
            'seller': '.seller-nick',
            'seller_rating': '.seller-rate',
            'image': '.search-item-pic img',
            'detail_link': '.search-item-title a',
            'isbn': '.attributes .isbn',
            'publisher': '.attributes .publisher',
            'publish_date': '.attributes .publish-date'
        },
        rate_limit=20,
        enabled=True,
        requires_auth=True
    )
}

# 平台优先级（按数据质量和更新频率排序）
PLATFORM_PRIORITY: List[str] = ['kongfuzi', 'duozhuayu', 'xianyu']

# 平台映射（平台名称到配置的映射）
PLATFORM_NAME_MAP: Dict[str, str] = {
    '孔夫子旧书网': 'kongfuzi',
    '多抓鱼': 'duozhuayu',
    '闲鱼': 'xianyu',
    'kongfuzi': 'kongfuzi',
    'duozhuayu': 'duozhuayu',
    'xianyu': 'xianyu',
    'goofish': 'xianyu'
}

# 获取启用的平台
def get_enabled_platforms() -> List[str]:
    """获取所有启用的平台"""
    return [platform_id for platform_id, config in PLATFORMS.items() if config.enabled]

# 获取平台配置
def get_platform_config(platform_id: str) -> PlatformConfig:
    """获取指定平台的配置"""
    return PLATFORMS.get(platform_id)

# 根据名称获取平台ID
def get_platform_id_by_name(platform_name: str) -> str:
    """根据平台名称获取平台ID"""
    return PLATFORM_NAME_MAP.get(platform_name, platform_name.lower())