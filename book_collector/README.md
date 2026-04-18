# 二手书信息采集系统

## 系统概述
本系统用于从多个二手书交易平台（孔夫子旧书网、多抓鱼、闲鱼等）自动采集二手书价格信息、封面图片，并将数据批量上传至指定数据库系统。

## 功能特性
- 多平台数据采集（孔夫子旧书网、多抓鱼、闲鱼等）
- 自动采集书籍价格信息（原价、二手售价、成色描述、卖家信息等）
- 封面图片自动下载和存储
- 数据整理和批量上传
- 定期自动更新机制
- 数据校验功能
- 日志记录和错误处理

## 系统架构
```
book_collector/
├── config/              # 配置文件
│   ├── __init__.py
│   ├── settings.py      # 系统配置
│   └── platforms.py    # 平台配置
├── collectors/          # 采集器模块
│   ├── __init__.py
│   ├── base.py         # 基础采集器
│   ├── kongfuzi.py    # 孔夫子旧书网采集器
│   ├── duozhuayu.py   # 多抓鱼采集器
│   ├── xianyu.py       # 闲鱼采集器
│   └── images.py       # 图片采集器
├── processors/          # 数据处理模块
│   ├── __init__.py
│   ├── validator.py    # 数据校验
│   ├── normalizer.py   # 数据标准化
│   └── uploader.py     # 数据上传器
├── models/             # 数据模型
│   ├── __init__.py
│   └── book.py        # 书籍数据模型
├── utils/              # 工具模块
│   ├── __init__.py
│   ├── logger.py       # 日志工具
│   ├── storage.py      # 存储工具
│   └── scheduler.py    # 定时任务
├── main.py             # 主程序入口
└── requirements.txt     # 依赖包
```

## 数据结构
```python
{
    "book_id": str,              # 书籍唯一标识
    "title": str,               # 书名
    "author": str,              # 作者
    "publisher": str,           # 出版社
    "publish_date": str,        # 出版日期
    "isbn": str,               # ISBN编号
    "original_price": float,      # 原价
    "secondhand_price": float,   # 二手售价
    "condition": str,           # 成色描述
    "condition_score": int,       # 成色评分（1-10）
    "seller_info": {            # 卖家信息
        "name": str,           # 卖家名称
        "rating": float,        # 卖家评分
        "sales_count": int,     # 销售数量
        "location": str         # 所在地
    },
    "platform": str,            # 来源平台
    "platform_url": str,        # 平台链接
    "cover_image": str,         # 封面图片路径
    "description": str,         # 书籍描述
    "tags": List[str],          # 标签
    "category": str,            # 分类
    "stock_status": str,        # 库存状态
    "collected_at": datetime,    # 采集时间
    "updated_at": datetime      # 更新时间
}
```

## 使用方法
```bash
# 安装依赖
pip install -r requirements.txt

# 运行采集系统
python main.py

# 定时任务（使用cron或系统计划任务）
# 每天凌晨2点运行
0 2 * * * python main.py
```

## 配置说明
编辑 `config/settings.py` 文件来配置：
- 数据库连接信息
- 图片存储路径
- 采集间隔时间
- 数据校验规则
- 平台API密钥（如需要）

## 注意事项
1. 请遵守各平台的使用条款和robots.txt规则
2. 设置合理的采集间隔，避免对目标网站造成压力
3. 定期检查数据质量，确保采集信息的准确性
4. 妥善保管API密钥和数据库凭证