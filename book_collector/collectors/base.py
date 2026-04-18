"""
基础采集器
提供通用的采集功能和接口
"""
import asyncio
import aiohttp
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import random
from config.settings import COLLECTION_CONFIG, SECURITY_CONFIG
from config.platforms import PlatformConfig, get_platform_config
from models.book import BookData, CollectionResult

logger = logging.getLogger(__name__)

class BaseCollector(ABC):
    """基础采集器抽象类"""
    
    def __init__(self, platform_id: str):
        self.platform_id = platform_id
        self.config: PlatformConfig = get_platform_config(platform_id)
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            'User-Agent': COLLECTION_CONFIG['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.init_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close_session()
    
    async def init_session(self):
        """初始化HTTP会话"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=COLLECTION_CONFIG['concurrent_requests'],
                ssl=SECURITY_CONFIG['verify_ssl'],
                force_close=True,
                enable_cleanup_closed=True
            )
            timeout = aiohttp.ClientTimeout(total=COLLECTION_CONFIG['timeout'])
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.headers
            )
            logger.info(f"初始化{self.config.name}采集器会话")
    
    async def close_session(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info(f"关闭{self.config.name}采集器会话")
    
    async def get_page(self, url: str, retries: int = 0) -> Optional[str]:
        """获取页面内容"""
        if retries >= COLLECTION_CONFIG['max_retries']:
            logger.error(f"获取页面失败，已达最大重试次数: {url}")
            return None
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.debug(f"成功获取页面: {url}")
                    return content
                elif response.status == 429:
                    # 请求过于频繁，等待后重试
                    wait_time = 2 ** retries + random.uniform(0, 1)
                    logger.warning(f"请求过于频繁，等待{wait_time:.1f}秒后重试: {url}")
                    await asyncio.sleep(wait_time)
                    return await self.get_page(url, retries + 1)
                else:
                    logger.warning(f"获取页面失败，状态码: {response.status}, URL: {url}")
                    return None
        except Exception as e:
            logger.error(f"获取页面异常: {url}, 错误: {str(e)}")
            await asyncio.sleep(1)
            return await self.get_page(url, retries + 1)
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """解析HTML内容"""
        return BeautifulSoup(html, 'html.parser')
    
    def extract_text(self, element) -> str:
        """提取元素文本"""
        if element:
            return element.get_text(strip=True)
        return ""
    
    def extract_url(self, element, base_url: str) -> Optional[str]:
        """提取URL"""
        if element:
            href = element.get('href') or element.get('src')
            if href:
                return urljoin(base_url, href)
        return None
    
    def extract_price(self, price_text: str) -> Optional[float]:
        """提取价格"""
        if not price_text:
            return None
        
        # 移除货币符号和空格
        price_text = price_text.replace('¥', '').replace('￥', '').replace('元', '').strip()
        
        try:
            return float(price_text)
        except ValueError:
            logger.warning(f"无法解析价格: {price_text}")
            return None
    
    def extract_condition_score(self, condition_text: str) -> int:
        """根据成色描述提取评分"""
        condition_map = {
            '全新': 10,
            '九成新': 9,
            '八成新': 8,
            '七成新': 7,
            '六成新': 6,
            '五成新': 5,
            '四成新': 4,
            '三成新': 3,
            '二成新': 2,
            '一成新': 1
        }
        
        for key, score in condition_map.items():
            if key in condition_text:
                return score
        
        # 如果无法匹配，返回默认分数
        return 7
    
    async def delay_request(self):
        """请求延迟"""
        delay = COLLECTION_CONFIG['delay_between_requests'] + random.uniform(0, 1)
        await asyncio.sleep(delay)
    
    @abstractmethod
    async def search_books(self, keyword: str, page: int = 1) -> List[BookData]:
        """搜索书籍"""
        pass
    
    @abstractmethod
    async def get_book_detail(self, book_id: str) -> Optional[BookData]:
        """获取书籍详情"""
        pass
    
    @abstractmethod
    async def collect_books(self, keywords: List[str], max_pages: int = 5) -> CollectionResult:
        """采集书籍"""
        pass
    
    async def download_image(self, image_url: str, save_path: str) -> bool:
        """下载图片"""
        try:
            async with self.session.get(image_url) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(save_path, 'wb') as f:
                        f.write(content)
                    logger.debug(f"成功下载图片: {image_url} -> {save_path}")
                    return True
                else:
                    logger.warning(f"下载图片失败，状态码: {response.status}, URL: {image_url}")
                    return False
        except Exception as e:
            logger.error(f"下载图片异常: {image_url}, 错误: {str(e)}")
            return False
    
    def generate_book_id(self, platform: str, book_url: str) -> str:
        """生成书籍唯一标识"""
        import hashlib
        url_hash = hashlib.md5(book_url.encode()).hexdigest()[:8]
        return f"{platform}_{url_hash}"