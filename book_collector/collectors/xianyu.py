"""
闲鱼采集器
"""
import logging
from typing import List, Optional
from urllib.parse import urljoin
from collectors.base import BaseCollector
from models.book import BookData, CollectionResult, SellerInfo
from config.platforms import get_platform_config

logger = logging.getLogger(__name__)

class XianyuCollector(BaseCollector):
    """闲鱼采集器"""
    
    def __init__(self):
        super().__init__('xianyu')
        
        # 闲鱼需要特殊的headers
        self.headers.update({
            'Referer': 'https://www.goofish.com/',
            'Origin': 'https://www.goofish.com',
        })
    
    async def search_books(self, keyword: str, page: int = 1) -> List[BookData]:
        """搜索书籍"""
        search_url = f"{self.config.search_url}?q={keyword}&page={page}"
        
        html = await self.get_page(search_url)
        if not html:
            return []
        
        soup = self.parse_html(html)
        book_elements = soup.select(self.config.selectors['book_list'])
        
        books = []
        for element in book_elements:
            try:
                book = await self.parse_book_element(element)
                if book:
                    books.append(book)
            except Exception as e:
                logger.error(f"解析书籍元素失败: {str(e)}")
                continue
        
        await self.delay_request()
        return books
    
    async def parse_book_element(self, element) -> Optional[BookData]:
        """解析书籍元素"""
        try:
            # 提取基本信息
            title_element = element.select_one(self.config.selectors['title'])
            title = self.extract_text(title_element)
            
            price_element = element.select_one(self.config.selectors['price'])
            secondhand_price = self.extract_price(self.extract_text(price_element))
            
            original_price_element = element.select_one(self.config.selectors['original_price'])
            original_price = self.extract_price(self.extract_text(original_price_element))
            
            if not title or not secondhand_price:
                logger.warning(f"书籍信息不完整: title={title}, price={secondhand_price}")
                return None
            
            # 提取链接
            detail_link_element = element.select_one(self.config.selectors['detail_link'])
            detail_url = self.extract_url(detail_link_element, self.config.base_url)
            
            if not detail_url:
                logger.warning(f"无法获取详情链接: {title}")
                return None
            
            # 提取图片
            image_element = element.select_one(self.config.selectors['image'])
            image_url = self.extract_url(image_element, self.config.base_url)
            
            # 提取成色
            condition_element = element.select_one(self.config.selectors['condition'])
            condition = self.extract_text(condition_element)
            condition_score = self.extract_condition_score(condition)
            
            # 提取卖家信息
            seller_element = element.select_one(self.config.selectors['seller'])
            seller_name = self.extract_text(seller_element)
            
            seller_rating_element = element.select_one(self.config.selectors['seller_rating'])
            seller_rating = self.extract_text(seller_rating_element)
            
            # 提取其他信息
            isbn_element = element.select_one(self.config.selectors['isbn'])
            isbn = self.extract_text(isbn_element)
            
            publisher_element = element.select_one(self.config.selectors['publisher'])
            publisher = self.extract_text(publisher_element)
            
            publish_date_element = element.select_one(self.config.selectors['publish_date'])
            publish_date = self.extract_text(publish_date_element)
            
            # 生成书籍ID
            book_id = self.generate_book_id('xianyu', detail_url)
            
            # 创建书籍数据对象
            book = BookData(
                book_id=book_id,
                title=title,
                author=None,
                publisher=publisher,
                publish_date=publish_date,
                isbn=isbn,
                original_price=original_price or secondhand_price,
                secondhand_price=secondhand_price,
                condition=condition,
                condition_score=condition_score,
                seller_info=SellerInfo(
                    name=seller_name,
                    rating=float(seller_rating) if seller_rating else None,
                    sales_count=None,
                    location=None,
                    response_rate=None
                ) if seller_name else None,
                platform='闲鱼',
                platform_url=detail_url,
                cover_image=None,
                description=None,
                tags=[],
                category=None,
                stock_status=None
            )
            
            # 下载封面图片
            if image_url:
                from config.settings import IMAGE_STORAGE
                import os
                from urllib.parse import urlparse
                
                parsed_url = urlparse(image_url)
                ext = os.path.splitext(parsed_url.path)[1][1:] or 'jpg'
                image_filename = f"{book_id}.{ext}"
                image_path = os.path.join(IMAGE_STORAGE['base_path'], image_filename)
                
                success = await self.download_image(image_url, image_path)
                if success:
                    book.cover_image = image_path
            
            return book
            
        except Exception as e:
            logger.error(f"解析书籍元素异常: {str(e)}")
            return None
    
    async def get_book_detail(self, book_id: str) -> Optional[BookData]:
        """获取书籍详情"""
        return None
    
    async def collect_books(self, keywords: List[str], max_pages: int = 5) -> CollectionResult:
        """采集书籍"""
        result = CollectionResult(
            success=False,
            platform=self.config.name,
            start_time=datetime.now()
        )
        
        logger.info(f"开始采集{self.config.name}，关键词: {keywords}")
        
        for keyword in keywords:
            logger.info(f"搜索关键词: {keyword}")
            
            for page in range(1, max_pages + 1):
                logger.info(f"采集第{page}页")
                
                books = await self.search_books(keyword, page)
                result.total_collected += len(books)
                
                for book in books:
                    try:
                        book.validate()
                        result.valid_count += 1
                        result.books.append(book)
                    except Exception as e:
                        logger.warning(f"数据校验失败: {book.title}, 错误: {str(e)}")
                        result.invalid_count += 1
                        result.errors.append(f"{book.title}: {str(e)}")
                
                logger.info(f"第{page}页采集完成，获得{len(books)}本书")
        
        result.success = result.valid_count > 0
        result.end_time = datetime.now()
        
        logger.info(f"{self.config.name}采集完成: 总计{result.total_collected}本，有效{result.valid_count}本，无效{result.invalid_count}本")
        
        return result