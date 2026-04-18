"""
数据上传器
将采集到的数据批量上传至指定数据库系统
"""
import logging
import aiohttp
import json
import gzip
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.book import BookData, UploadResult
from config.settings import UPLOAD_CONFIG

logger = logging.getLogger(__name__)

class DataUploader:
    """数据上传器"""
    
    def __init__(self):
        self.api_endpoint = UPLOAD_CONFIG['api_endpoint']
        self.api_key = UPLOAD_CONFIG['api_key']
        self.batch_size = UPLOAD_CONFIG['batch_size']
        self.max_retries = UPLOAD_CONFIG['max_retries']
        self.timeout = UPLOAD_CONFIG['timeout']
        self.compression = UPLOAD_CONFIG['compression']
        
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'BookCollector/1.0'
        }
        
        if self.compression:
            self.headers['Content-Encoding'] = 'gzip'
    
    async def upload_books(self, books: List[BookData]) -> UploadResult:
        """批量上传书籍数据"""
        result = UploadResult(
            success=False,
            start_time=datetime.now()
        )
        
        logger.info(f"开始上传书籍数据，总数: {len(books)}")
        
        # 分批上传
        for i in range(0, len(books), self.batch_size):
            batch = books[i:i + self.batch_size]
            batch_result = await self.upload_batch(batch)
            
            result.total_uploaded += len(batch)
            result.success_count += batch_result['success_count']
            result.failed_count += batch_result['failed_count']
            result.errors.extend(batch_result['errors'])
            
            logger.info(f"批次{i//self.batch_size + 1}上传完成: 成功{batch_result['success_count']}本，失败{batch_result['failed_count']}本")
        
        result.success = result.failed_count == 0
        result.end_time = datetime.now()
        
        logger.info(f"上传完成: 总计{result.total_uploaded}本，成功{result.success_count}本，失败{result.failed_count}本")
        
        return result
    
    async def upload_batch(self, books: List[BookData]) -> Dict[str, Any]:
        """上传单个批次"""
        batch_result = {
            'success_count': 0,
            'failed_count': 0,
            'errors': []
        }
        
        try:
            # 准备数据
            books_data = [book.to_dict() for book in books]
            
            # 压缩数据
            if self.compression:
                json_data = json.dumps(books_data, ensure_ascii=False)
                compressed_data = gzip.compress(json_data.encode('utf-8'))
            else:
                compressed_data = json.dumps(books_data, ensure_ascii=False).encode('utf-8')
            
            # 上传数据
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_endpoint,
                    data=compressed_data,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # 处理响应
                        if result.get('success'):
                            batch_result['success_count'] = len(books)
                        else:
                            batch_result['failed_count'] = len(books)
                            batch_result['errors'].append(result.get('message', '上传失败'))
                    elif response.status == 401:
                        batch_result['failed_count'] = len(books)
                        batch_result['errors'].append('API密钥无效')
                    elif response.status == 429:
                        batch_result['failed_count'] = len(books)
                        batch_result['errors'].append('请求过于频繁，请稍后重试')
                    else:
                        batch_result['failed_count'] = len(books)
                        error_text = await response.text()
                        batch_result['errors'].append(f'上传失败，状态码: {response.status}, 错误: {error_text}')
        
        except aiohttp.ClientError as e:
            batch_result['failed_count'] = len(books)
            batch_result['errors'].append(f'网络错误: {str(e)}')
        except json.JSONDecodeError as e:
            batch_result['failed_count'] = len(books)
            batch_result['errors'].append(f'JSON解析错误: {str(e)}')
        except Exception as e:
            batch_result['failed_count'] = len(books)
            batch_result['errors'].append(f'未知错误: {str(e)}')
        
        return batch_result
    
    async def upload_single_book(self, book: BookData) -> bool:
        """上传单本书籍"""
        try:
            # 准备数据
            book_data = book.to_dict()
            
            # 压缩数据
            if self.compression:
                json_data = json.dumps(book_data, ensure_ascii=False)
                compressed_data = gzip.compress(json_data.encode('utf-8'))
            else:
                compressed_data = json.dumps(book_data, ensure_ascii=False).encode('utf-8')
            
            # 上传数据
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_endpoint,
                    data=compressed_data,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return result.get('success', False)
                    else:
                        logger.warning(f"上传书籍失败: {book.title}, 状态码: {response.status}")
                        return False
        
        except Exception as e:
            logger.error(f"上传书籍异常: {book.title}, 错误: {str(e)}")
            return False
    
    async def check_api_health(self) -> bool:
        """检查API健康状态"""
        try:
            health_url = f"{self.api_endpoint}/health"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    health_url,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        return True
                    else:
                        logger.warning(f"API健康检查失败，状态码: {response.status}")
                        return False
        
        except Exception as e:
            logger.error(f"API健康检查异常: {str(e)}")
            return False
    
    async def get_upload_stats(self) -> Optional[Dict[str, Any]]:
        """获取上传统计信息"""
        try:
            stats_url = f"{self.api_endpoint}/stats"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    stats_url,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"获取统计信息失败，状态码: {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"获取统计信息异常: {str(e)}")
            return None
    
    async def retry_upload(self, books: List[BookData], failed_books: List[BookData]) -> UploadResult:
        """重试上传失败的书籍"""
        if not failed_books:
            return UploadResult(success=True, total_uploaded=0, success_count=0, failed_count=0)
        
        logger.info(f"重试上传失败的书籍，数量: {len(failed_books)}")
        
        retry_result = UploadResult(
            success=False,
            start_time=datetime.now()
        )
        
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"重试第{attempt}次")
            
            result = await self.upload_books(failed_books)
            retry_result.total_uploaded += result.total_uploaded
            retry_result.success_count += result.success_count
            retry_result.failed_count += result.failed_count
            retry_result.errors.extend(result.errors)
            
            # 如果全部成功，停止重试
            if result.failed_count == 0:
                break
            
            # 如果不是最后一次重试，更新失败书籍列表
            if attempt < self.max_retries:
                # 从原始书籍中找出失败的书籍
                failed_indices = [i for i, error in enumerate(result.errors) if error]
                failed_books = [books[i] for i in failed_indices if i < len(books)]
        
        retry_result.success = retry_result.failed_count == 0
        retry_result.end_time = datetime.now()
        
        logger.info(f"重试上传完成: 成功{retry_result.success_count}本，失败{retry_result.failed_count}本")
        
        return retry_result