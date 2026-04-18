"""
定时任务模块
实现定期自动更新机制
"""
import logging
import asyncio
from typing import List, Optional, Callable
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config.settings import SCHEDULER_CONFIG
from config.platforms import get_enabled_platforms
from collectors.kongfuzi import KongfuziCollector
from collectors.duozhuayu import DuozhuayuCollector
from collectors.xianyu import XianyuCollector
from processors.validator import DataValidator
from processors.normalizer import DataNormalizer
from processors.uploader import DataUploader
from models.book import BookData

logger = logging.getLogger(__name__)

class TaskScheduler:
    """定时任务调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.validator = DataValidator()
        self.normalizer = DataNormalizer()
        self.uploader = DataUploader()
        
        self.collectors = {
            'kongfuzi': KongfuziCollector(),
            'duozhuayu': DuozhuayuCollector(),
            'xianyu': XianyuCollector()
        }
        
        self.collection_keywords = [
            'Python编程', '算法导论', '考研数学', 'JavaScript',
            '数据结构', '计算机等级考试', '公务员考试',
            '英语四级', '考研英语', '高等数学'
        ]
        
        self.max_pages = 5
        self.is_running = False
    
    async def start(self):
        """启动定时任务"""
        if self.is_running:
            logger.warning("定时任务已在运行")
            return
        
        if not SCHEDULER_CONFIG['enabled']:
            logger.info("定时任务功能已禁用")
            return
        
        self.is_running = True
        
        # 添加数据采集任务
        self.scheduler.add_job(
            self.collect_data,
            trigger=IntervalTrigger(seconds=SCHEDULER_CONFIG['collection_interval']),
            id='collect_data',
            name='数据采集任务',
            replace_existing=True
        )
        
        # 添加数据更新任务
        self.scheduler.add_job(
            self.update_data,
            trigger=IntervalTrigger(seconds=SCHEDULER_CONFIG['update_interval']),
            id='update_data',
            name='数据更新任务',
            replace_existing=True
        )
        
        # 添加数据清理任务
        self.scheduler.add_job(
            self.cleanup_data,
            trigger=IntervalTrigger(seconds=SCHEDULER_CONFIG['cleanup_interval']),
            id='cleanup_data',
            name='数据清理任务',
            replace_existing=True
        )
        
        # 启动调度器
        self.scheduler.start()
        
        logger.info("定时任务调度器已启动")
        logger.info(f"数据采集间隔: {SCHEDULER_CONFIG['collection_interval']}秒")
        logger.info(f"数据更新间隔: {SCHEDULER_CONFIG['update_interval']}秒")
        logger.info(f"数据清理间隔: {SCHEDULER_CONFIG['cleanup_interval']}秒")
        
        # 立即执行一次采集
        await self.collect_data()
    
    async def stop(self):
        """停止定时任务"""
        if not self.is_running:
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        
        logger.info("定时任务调度器已停止")
    
    async def collect_data(self):
        """采集数据任务"""
        logger.info("=" * 50)
        logger.info("开始执行数据采集任务")
        logger.info(f"执行时间: {datetime.now()}")
        logger.info("=" * 50)
        
        all_books = []
        
        # 遍历所有启用的平台
        for platform_id in get_enabled_platforms():
            logger.info(f"开始采集{platform_id}平台")
            
            collector = self.collectors.get(platform_id)
            if not collector:
                logger.warning(f"未找到{platform_id}采集器")
                continue
            
            try:
                async with collector:
                    # 采集书籍数据
                    result = await collector.collect_books(
                        keywords=self.collection_keywords,
                        max_pages=self.max_pages
                    )
                    
                    # 记录采集结果
                    logger.info(f"{platform_id}采集结果:")
                    logger.info(f"  总计: {result.total_collected}本")
                    logger.info(f"  有效: {result.valid_count}本")
                    logger.info(f"  无效: {result.invalid_count}本")
                    logger.info(f"  耗时: {result.duration:.2f}秒")
                    logger.info(f"  成功率: {result.success_rate:.1f}%")
                    
                    # 添加到总列表
                    all_books.extend(result.books)
                    
            except Exception as e:
                logger.error(f"采集{platform_id}平台失败: {str(e)}")
                continue
        
        # 数据校验
        logger.info("开始数据校验")
        validation_result = self.validator.validate_batch(all_books)
        logger.info(f"校验结果: 总计{validation_result['total']}本，有效{validation_result['valid']}本，无效{validation_result['invalid']}本")
        
        # 提取有效数据
        valid_books = [book for book in all_books if book.book_id not in [error['book_id'] for error in validation_result['error_details']]]
        
        # 数据标准化
        logger.info("开始数据标准化")
        normalized_books = self.normalizer.normalize_books(valid_books)
        
        # 合并重复数据
        logger.info("开始合并重复数据")
        merged_books = self.normalizer.merge_duplicate_books(normalized_books)
        
        # 数据上传
        logger.info("开始数据上传")
        upload_result = await self.uploader.upload_books(merged_books)
        
        logger.info(f"上传结果: 总计{upload_result.total_uploaded}本，成功{upload_result.success_count}本，失败{upload_result.failed_count}本")
        
        # 记录任务完成
        logger.info("=" * 50)
        logger.info("数据采集任务完成")
        logger.info(f"完成时间: {datetime.now()}")
        logger.info(f"总耗时: {upload_result.duration:.2f}秒")
        logger.info("=" * 50)
    
    async def update_data(self):
        """更新数据任务"""
        logger.info("=" * 50)
        logger.info("开始执行数据更新任务")
        logger.info(f"执行时间: {datetime.now()}")
        logger.info("=" * 50)
        
        # 这里可以实现数据更新逻辑
        # 例如：检查已采集书籍的价格变化、库存状态等
        
        logger.info("数据更新任务完成")
        logger.info(f"完成时间: {datetime.now()}")
        logger.info("=" * 50)
    
    async def cleanup_data(self):
        """清理数据任务"""
        logger.info("=" * 50)
        logger.info("开始执行数据清理任务")
        logger.info(f"执行时间: {datetime.now()}")
        logger.info("=" * 50)
        
        cleanup_days = SCHEDULER_CONFIG['cleanup_days']
        cutoff_date = datetime.now() - timedelta(days=cleanup_days)
        
        logger.info(f"清理{cleanup_days}天前的数据（{cutoff_date}之前）")
        
        # 这里可以实现数据清理逻辑
        # 例如：删除过期的临时文件、清理缓存等
        
        logger.info("数据清理任务完成")
        logger.info(f"完成时间: {datetime.now()}")
        logger.info("=" * 50)
    
    async def manual_collect(self, keywords: Optional[List[str]] = None, max_pages: int = 5):
        """手动执行采集任务"""
        if keywords:
            self.collection_keywords = keywords
        
        self.max_pages = max_pages
        
        logger.info("手动执行数据采集")
        await self.collect_data()
    
    def add_collection_job(self, func: Callable, interval: int, job_id: str):
        """添加自定义采集任务"""
        self.scheduler.add_job(
            func,
            trigger=IntervalTrigger(seconds=interval),
            id=job_id,
            name=f'自定义任务-{job_id}',
            replace_existing=True
        )
        
        logger.info(f"已添加自定义任务: {job_id}, 间隔: {interval}秒")
    
    def remove_job(self, job_id: str):
        """移除任务"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"已移除任务: {job_id}")
        except Exception as e:
            logger.error(f"移除任务失败: {job_id}, 错误: {str(e)}")
    
    def get_jobs(self) -> List[dict]:
        """获取所有任务"""
        jobs = []
        
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger)
            })
        
        return jobs
    
    def pause_job(self, job_id: str):
        """暂停任务"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"已暂停任务: {job_id}")
        except Exception as e:
            logger.error(f"暂停任务失败: {job_id}, 错误: {str(e)}")
    
    def resume_job(self, job_id: str):
        """恢复任务"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"已恢复任务: {job_id}")
        except Exception as e:
            logger.error(f"恢复任务失败: {job_id}, 错误: {str(e)}")