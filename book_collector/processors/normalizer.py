"""
数据标准化模块
将采集到的数据转换为统一格式
"""
import logging
from typing import List, Dict, Any
from datetime import datetime
from models.book import BookData
from processors.validator import DataValidator

logger = logging.getLogger(__name__)

class DataNormalizer:
    """数据标准化器"""
    
    def __init__(self):
        self.validator = DataValidator()
    
    def normalize_books(self, books: List[BookData]) -> List[BookData]:
        """标准化书籍数据列表"""
        normalized_books = []
        
        for book in books:
            try:
                # 标准化单本书籍
                normalized_book = self.normalize_book(book)
                normalized_books.append(normalized_book)
            except Exception as e:
                logger.error(f"标准化书籍失败: {book.title}, 错误: {str(e)}")
                continue
        
        logger.info(f"标准化完成: {len(normalized_books)}/{len(books)}本")
        return normalized_books
    
    def normalize_book(self, book: BookData) -> BookData:
        """标准化单本书籍数据"""
        # 使用校验器的标准化功能
        normalized_book = self.validator.normalize_data(book)
        
        # 补充缺失字段
        if not normalized_book.collected_at:
            normalized_book.collected_at = datetime.now()
        
        if not normalized_book.updated_at:
            normalized_book.updated_at = datetime.now()
        
        # 标准化分类
        if not normalized_book.category:
            normalized_book.category = self._infer_category(normalized_book)
        
        # 生成标签
        if not normalized_book.tags:
            normalized_book.tags = self._generate_tags(normalized_book)
        
        # 标准化库存状态
        if not normalized_book.stock_status:
            normalized_book.stock_status = self._infer_stock_status(normalized_book)
        
        return normalized_book
    
    def _infer_category(self, book: BookData) -> str:
        """推断书籍分类"""
        title = book.title.lower() if book.title else ""
        description = book.description.lower() if book.description else ""
        
        # 分类关键词映射
        category_keywords = {
            '教材': ['教材', '课本', '教科书', '大学', '研究生', '高职', '中职'],
            '考试': ['考研', '公务员', '司法', '会计', '教师资格', '医学考试', '计算机等级', '英语', '托福', '雅思'],
            '专业书籍': ['编程', '算法', '数据结构', '计算机', '软件', '网络', '数据库', '人工智能', '机器学习'],
            '文学': ['小说', '散文', '诗歌', '文学', '名著', '经典'],
            '经管': ['经济', '管理', '金融', '会计', '营销', '人力资源'],
            '理工': ['数学', '物理', '化学', '生物', '工程', '机械', '电子'],
            '医学': ['医学', '护理', '药学', '临床', '解剖', '病理'],
            '其他': []
        }
        
        # 根据关键词推断分类
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in title or keyword in description:
                    return category
        
        return '其他'
    
    def _generate_tags(self, book: BookData) -> List[str]:
        """生成书籍标签"""
        tags = []
        
        # 根据成色生成标签
        if book.condition:
            tags.append(book.condition)
        
        # 根据价格生成标签
        if book.secondhand_price:
            if book.secondhand_price <= 10:
                tags.append('特价')
            elif book.secondhand_price <= 30:
                tags.append('实惠')
            elif book.secondhand_price <= 100:
                tags.append('中等价位')
            else:
                tags.append('高价')
        
        # 根据卖家评分生成标签
        if book.seller_info and book.seller_info.rating:
            if book.seller_info.rating >= 4.5:
                tags.append('优质卖家')
            elif book.seller_info.rating >= 4.0:
                tags.append('信誉良好')
        
        # 根据成色评分生成标签
        if book.condition_score:
            if book.condition_score >= 9:
                tags.append('全新')
            elif book.condition_score >= 7:
                tags.append('成色好')
            elif book.condition_score >= 5:
                tags.append('成色一般')
            else:
                tags.append('成色较差')
        
        # 去重
        tags = list(set(tags))
        
        return tags
    
    def _infer_stock_status(self, book: BookData) -> str:
        """推断库存状态"""
        # 默认为在售
        return '在售'
    
    def merge_duplicate_books(self, books: List[BookData]) -> List[BookData]:
        """合并重复书籍数据"""
        book_map = {}
        
        for book in books:
            book_id = book.book_id
            
            if book_id in book_map:
                # 合并数据，保留最新和更完整的信息
                existing_book = book_map[book_id]
                
                # 保留更新的采集时间
                if book.collected_at > existing_book.collected_at:
                    book_map[book_id] = book
                else:
                    # 合并卖家信息
                    if book.seller_info and not existing_book.seller_info:
                        existing_book.seller_info = book.seller_info
            else:
                book_map[book_id] = book
        
        merged_books = list(book_map.values())
        logger.info(f"合并重复数据: {len(books)} -> {len(merged_books)}")
        
        return merged_books
    
    def sort_books(self, books: List[BookData], sort_by: str = 'collected_at', reverse: bool = True) -> List[BookData]:
        """排序书籍数据"""
        if sort_by == 'price':
            return sorted(books, key=lambda x: x.secondhand_price, reverse=reverse)
        elif sort_by == 'price_ratio':
            return sorted(books, key=lambda x: x.secondhand_price / x.original_price if x.original_price else 0, reverse=reverse)
        elif sort_by == 'condition':
            return sorted(books, key=lambda x: x.condition_score or 0, reverse=reverse)
        elif sort_by == 'seller_rating':
            return sorted(books, key=lambda x: x.seller_info.rating if x.seller_info else 0, reverse=reverse)
        elif sort_by == 'collected_at':
            return sorted(books, key=lambda x: x.collected_at, reverse=reverse)
        else:
            return books
    
    def filter_books(self, books: List[BookData], filters: Dict[str, Any]) -> List[BookData]:
        """过滤书籍数据"""
        filtered_books = books
        
        # 价格范围过滤
        if 'min_price' in filters:
            filtered_books = [book for book in filtered_books if book.secondhand_price >= filters['min_price']]
        if 'max_price' in filters:
            filtered_books = [book for book in filtered_books if book.secondhand_price <= filters['max_price']]
        
        # 成色过滤
        if 'min_condition' in filters:
            filtered_books = [book for book in filtered_books if (book.condition_score or 0) >= filters['min_condition']]
        if 'max_condition' in filters:
            filtered_books = [book for book in filtered_books if (book.condition_score or 0) <= filters['max_condition']]
        
        # 平台过滤
        if 'platforms' in filters:
            filtered_books = [book for book in filtered_books if book.platform in filters['platforms']]
        
        # 分类过滤
        if 'categories' in filters:
            filtered_books = [book for book in filtered_books if book.category in filters['categories']]
        
        # 标签过滤
        if 'tags' in filters:
            filtered_books = [book for book in filtered_books if any(tag in book.tags for tag in filters['tags'])]
        
        # 卖家评分过滤
        if 'min_seller_rating' in filters:
            filtered_books = [book for book in filtered_books if book.seller_info and book.seller_info.rating >= filters['min_seller_rating']]
        
        logger.info(f"过滤数据: {len(books)} -> {len(filtered_books)}")
        return filtered_books