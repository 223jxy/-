from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.exc import SQLAlchemyError

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import SQLALCHEMY_DATABASE_URL
from app.utils.logger import logger_instance
from app.utils.monitoring import monitoring

# 创建数据库引擎，配置连接池
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建线程安全的会话工厂
ScopedSession = scoped_session(SessionLocal)

# 创建基类
Base = declarative_base()

# 依赖项，用于获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        # 测试数据库连接
        db.execute("SELECT 1")
        yield db
    except SQLAlchemyError as e:
        logger_instance.error(f"Database connection failed: {e}")
        # 触发数据库连接失败告警
        monitoring.check_database_connection(False)
        raise
    finally:
        try:
            db.close()
        except SQLAlchemyError as e:
            logger_instance.error(f"Failed to close database connection: {e}")