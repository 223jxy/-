"""
数据校验模块
验证采集数据的准确性和完整性
"""
import logging
import re
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.book import BookData, SellerInfo
from config.settings import VALIDATION_CONFIG

logger = logging.getLogger(__name__)

class DataValidator:
    """数据校验器"""
    
    def __init__(self):
        self.validation_rules = VALIDATION_CONFIG
    
    def validate_book(self, book: BookData) -> tuple[bool, List[str]]:
        """校验单本书籍数据"""
        errors = []
        
        # 必填字段校验
        for field in self.validation_rules['required_fields']:
            if not hasattr(book, field) or getattr(book, field) is None:
                errors.append(f"缺少必填字段: {field}")
        
        # 价格校验
        if book.original_price and book.secondhand_price:
            if book.original_price < self.validation_rules['min_price']:
                errors.append(f"原价过低: {book.original_price}")
            elif book.original_price > self.validation_rules['max_price']:
                errors.append(f"原价过高: {book.original_price}")
            
            if book.secondhand_price < self.validation_rules['min_price']:
                errors.append(f"二手价过低: {book.secondhand_price}")
            elif book.secondhand_price > self.validation_rules['max_price']:
                errors.append(f"二手价过高: {book.secondhand_price}")
            
            # 价格比例校验
            price_ratio = book.secondhand_price / book.original_price
            min_ratio, max_ratio = self.validation_rules['price_ratio_range']
            if not (min_ratio <= price_ratio <= max_ratio):
                errors.append(f"二手价与原价比例异常: {price_ratio:.2f}")
        
        # 标题校验
        if book.title:
            if len(book.title) < self.validation_rules['min_title_length']:
                errors.append(f"标题过短: {book.title}")
            elif len(book.title) > self.validation_rules['max_title_length']:
                errors.append(f"标题过长: {book.title}")
        
        # ISBN校验
        if book.isbn:
            isbn_pattern = self.validation_rules['isbn_pattern']
            if not re.match(isbn_pattern, book.isbn):
                errors.append(f"ISBN格式不正确: {book.isbn}")
        
        # 卖家信息校验
        if book.seller_info:
            if not book.seller_info.name:
                errors.append("卖家名称不能为空")
            
            if book.seller_info.rating is not None:
                if book.seller_info.rating < 0 or book.seller_info.rating > 5:
                    errors.append(f"卖家评分异常: {book.seller_info.rating}")
            
            if book.seller_info.sales_count is not None and book.seller_info.sales_count < 0:
                errors.append(f"销售数量异常: {book.seller_info.sales_count}")
        
        # 成色校验
        if book.condition_score is not None:
            if book.condition_score < 1 or book.condition_score > 10:
                errors.append(f"成色评分异常: {book.condition_score}")
        
        # URL校验
        if book.platform_url:
            if not self._is_valid_url(book.platform_url):
                errors.append(f"平台链接格式不正确: {book.platform_url}")
        
        # 日期校验
        if book.publish_date:
            if not self._is_valid_date(book.publish_date):
                errors.append(f"出版日期格式不正确: {book.publish_date}")
        
        # 标签校验
        if book.tags:
            if len(book.tags) > 10:
                errors.append(f"标签数量过多: {len(book.tags)}")
            
            for tag in book.tags:
                if not isinstance(tag, str) or len(tag) > 20:
                    errors.append(f"标签格式不正确: {tag}")
        
        # 描述校验
        if book.description and len(book.description) > 2000:
            errors.append(f"描述过长: {len(book.description)}字符")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_batch(self, books: List[BookData]) -> Dict[str, Any]:
        """批量校验书籍数据"""
        results = {
            'total': len(books),
            'valid': 0,
            'invalid': 0,
            'errors': [],
            'error_details': []
        }
        
        for book in books:
            is_valid, errors = self.validate_book(book)
            
            if is_valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
                results['error_details'].append({
                    'book_id': book.book_id,
                    'title': book.title,
                    'errors': errors
                })
                results['errors'].extend(errors)
        
        return results
    
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domain
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # top level domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
            r'(?::\d+)?'  # port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        return bool(url_pattern.match(url))
    
    def _is_valid_date(self, date_str: str) -> bool:
        """验证日期格式"""
        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y年%m月%d日',
            '%Y-%m',
            '%Y/%m'
        ]
        
        for date_format in date_formats:
            try:
                datetime.strptime(date_str, date_format)
                return True
            except ValueError:
                continue
        
        return False
    
    def normalize_data(self, book: BookData) -> BookData:
        """标准化数据"""
        # 标准化价格
        if book.original_price:
            book.original_price = round(book.original_price, 2)
        if book.secondhand_price:
            book.secondhand_price = round(book.secondhand_price, 2)
        
        # 标准化成色描述
        condition_map = {
            '全新': '全新',
            '99新': '九成新',
            '95新': '九成新',
            '90新': '九成新',
            '88新': '八成新',
            '85新': '八成新',
            '80新': '八成新',
            '75新': '七成新',
            '70新': '七成新',
            '6成新': '六成新及以下',
            '5成新': '六成新及以下'
        }
        
        if book.condition in condition_map:
            book.condition = condition_map[book.condition]
        
        # 标准化卖家评分
        if book.seller_info and book.seller_info.rating:
            book.seller_info.rating = round(book.seller_info.rating, 1)
        
        # 标准化标签
        book.tags = [tag.strip() for tag in book.tags if tag.strip()]
        book.tags = list(set(book.tags))  # 去重
        
        # 标准化文本
        if book.title:
            book.title = book.title.strip()
        if book.author:
            book.author = book.author.strip()
        if book.publisher:
            book.publisher = book.publisher.strip()
        if book.description:
            book.description = book.description.strip()
        
        return book
    
    def check_duplicates(self, books: List[BookData]) -> Dict[str, Any]:
        """检查重复数据"""
        book_ids = [book.book_id for book in books]
        platform_urls = [book.platform_url for book in books]
        
        duplicate_ids = self._find_duplicates(book_ids)
        duplicate_urls = self._find_duplicates(platform_urls)
        
        return {
            'has_duplicates': len(duplicate_ids) > 0 or len(duplicate_urls) > 0,
            'duplicate_ids': duplicate_ids,
            'duplicate_urls': duplicate_urls,
            'duplicate_count': len(duplicate_ids) + len(duplicate_urls)
        }
    
    def _find_duplicates(self, items: List[str]) -> List[str]:
        """查找重复项"""
        seen = set()
        duplicates = []
        
        for item in items:
            if item in seen:
                duplicates.append(item)
            else:
                seen.add(item)
        
        return duplicates