"""
二手书信息采集系统主程序
"""
import asyncio
import logging
import sys
import argparse
from typing import Optional, List
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import LOGGING_CONFIG, COLLECTION_CONFIG, SCHEDULER_CONFIG
from config.platforms import get_enabled_platforms, PLATFORM_PRIORITY
from collectors.kongfuzi import KongfuziCollector
from collectors.duozhuayu import DuozhuayuCollector
from collectors.xianyu import XianyuCollector
from processors.validator import DataValidator
from processors.normalizer import DataNormalizer
from processors.uploader import DataUploader
from utils.scheduler import TaskScheduler
from models.book import BookData, CollectionResult

# 配置日志
import logging.config
logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)

class BookCollectorSystem:
    """二手书采集系统主类"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.normalizer = DataNormalizer()
        self.uploader = DataUploader()
        self.scheduler = TaskScheduler()
        
        self.collectors = {
            'kongfuzi': KongfuziCollector(),
            'duozhuayu': DuozhuayuCollector(),
            'xianyu': XianyuCollector()
        }
        
        self.collection_keywords = [
            'Python编程', '算法导论', '考研数学', 'JavaScript',
            '数据结构', '计算机等级考试', '公务员考试',
            '英语四级', '考研英语', '高等数学',
            '经济学原理', '管理学', '会计学', '市场营销'
        ]
        
        self.max_pages = 5
    
    async def collect_single_platform(self, platform_id: str, keywords: List[str]) -> CollectionResult:
        """采集单个平台数据"""
        logger.info(f"开始采集{platform_id}平台")
        
        collector = self.collectors.get(platform_id)
        if not collector:
            logger.error(f"未找到{platform_id}采集器")
            return CollectionResult(success=False, platform=platform_id)
        
        try:
            async with collector:
                result = await collector.collect_books(
                    keywords=keywords,
                    max_pages=self.max_pages
                )
                
                logger.info(f"{platform_id}采集完成:")
                logger.info(f"  总计: {result.total_collected}本")
                logger.info(f"  有效: {result.valid_count}本")
                logger.info(f"  无效: {result.invalid_count}本")
                logger.info(f"  耗时: {result.duration:.2f}秒")
                logger.info(f"  成功率: {result.success_rate:.1f}%")
                
                return result
                
        except Exception as e:
            logger.error(f"采集{platform_id}平台失败: {str(e)}")
            return CollectionResult(success=False, platform=platform_id, errors=[str(e)])
    
    async def collect_all_platforms(self, keywords: Optional[List[str]] = None) -> List[CollectionResult]:
        """采集所有平台数据"""
        if keywords:
            self.collection_keywords = keywords
        
        logger.info("=" * 60)
        logger.info("开始采集所有平台数据")
        logger.info(f"采集关键词: {self.collection_keywords}")
        logger.info(f"最大页数: {self.max_pages}")
        logger.info(f"执行时间: {datetime.now()}")
        logger.info("=" * 60)
        
        results = []
        all_books = []
        
        # 按优先级顺序采集
        for platform_id in PLATFORM_PRIORITY:
            if platform_id not in get_enabled_platforms():
                logger.info(f"{platform_id}平台未启用，跳过")
                continue
            
            logger.info(f"正在采集{platform_id}平台...")
            
            result = await self.collect_single_platform(platform_id, self.collection_keywords)
            results.append(result)
            all_books.extend(result.books)
        
        logger.info("=" * 60)
        logger.info("所有平台采集完成")
        logger.info(f"总计采集: {len(all_books)}本书")
        logger.info("=" * 60)
        
        return results
    
    async def process_and_upload(self, books: List[BookData]) -> bool:
        """处理并上传数据"""
        logger.info("开始处理和上传数据")
        
        # 数据校验
        logger.info("步骤1: 数据校验")
        validation_result = self.validator.validate_batch(books)
        logger.info(f"  总计: {validation_result['total']}本")
        logger.info(f"  有效: {validation_result['valid']}本")
        logger.info(f"  无效: {validation_result['invalid']}本")
        
        # 提取有效数据
        valid_books = [book for book in books if book.book_id not in [error['book_id'] for error in validation_result['error_details']]]
        
        if not valid_books:
            logger.warning("没有有效数据，跳过上传")
            return False
        
        # 数据标准化
        logger.info("步骤2: 数据标准化")
        normalized_books = self.normalizer.normalize_books(valid_books)
        
        # 合并重复数据
        logger.info("步骤3: 合并重复数据")
        merged_books = self.normalizer.merge_duplicate_books(normalized_books)
        
        # 数据上传
        logger.info("步骤4: 数据上传")
        upload_result = await self.uploader.upload_books(merged_books)
        
        logger.info(f"上传结果: 成功{upload_result.success_count}本，失败{upload_result.failed_count}本")
        
        return upload_result.success
    
    async def run_collection(self, keywords: Optional[List[str]] = None):
        """运行完整的采集流程"""
        try:
            # 采集数据
            results = await self.collect_all_platforms(keywords)
            
            # 收集所有书籍
            all_books = []
            for result in results:
                all_books.extend(result.books)
            
            if not all_books:
                logger.warning("未采集到任何数据")
                return
            
            # 处理和上传数据
            success = await self.process_and_upload(all_books)
            
            if success:
                logger.info("采集和上传流程成功完成")
            else:
                logger.error("采集和上传流程失败")
                
        except Exception as e:
            logger.error(f"运行采集流程失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    async def start_scheduler(self):
        """启动定时任务"""
        logger.info("启动定时任务调度器")
        await self.scheduler.start()
    
    async def stop_scheduler(self):
        """停止定时任务"""
        logger.info("停止定时任务调度器")
        await self.scheduler.stop()
    
    def print_system_info(self):
        """打印系统信息"""
        logger.info("=" * 60)
        logger.info("二手书信息采集系统")
        logger.info("=" * 60)
        logger.info(f"系统版本: 1.0.0")
        logger.info(f"执行时间: {datetime.now()}")
        logger.info(f"启用的平台: {', '.join(get_enabled_platforms())}")
        logger.info(f"采集间隔: {SCHEDULER_CONFIG['collection_interval']}秒")
        logger.info(f"更新间隔: {SCHEDULER_CONFIG['update_interval']}秒")
        logger.info(f"清理间隔: {SCHEDULER_CONFIG['cleanup_interval']}秒")
        logger.info(f"批量大小: {COLLECTION_CONFIG['batch_size']}")
        logger.info(f"最大重试: {COLLECTION_CONFIG['max_retries']}次")
        logger.info("=" * 60)

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='二手书信息采集系统')
    parser.add_argument('--mode', '-m', choices=['collect', 'scheduler', 'manual'], 
                       default='collect', help='运行模式')
    parser.add_argument('--keywords', '-k', nargs='+', help='采集关键词')
    parser.add_argument('--platforms', '-p', nargs='+', help='指定平台')
    parser.add_argument('--pages', '-n', type=int, default=5, help='最大页数')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 创建系统实例
    system = BookCollectorSystem()
    
    # 打印系统信息
    system.print_system_info()
    
    try:
        if args.mode == 'collect':
            # 单次采集模式
            keywords = args.keywords if args.keywords else None
            max_pages = args.pages
            
            if max_pages:
                system.max_pages = max_pages
            
            await system.run_collection(keywords)
            
        elif args.mode == 'scheduler':
            # 定时任务模式
            await system.start_scheduler()
            
            # 保持运行
            try:
                while True:
                    await asyncio.sleep(60)
            except KeyboardInterrupt:
                logger.info("接收到中断信号，停止定时任务")
                await system.stop_scheduler()
                
        elif args.mode == 'manual':
            # 手动采集模式
            keywords = args.keywords if args.keywords else None
            max_pages = args.pages
            
            if max_pages:
                system.max_pages = max_pages
            
            await system.scheduler.manual_collect(keywords, max_pages)
            
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())