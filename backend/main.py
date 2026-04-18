from fastapi import FastAPI
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 检查是否在Docker环境中运行
is_docker = os.getenv('DOCKER_ENV', 'false').lower() == 'true'

if is_docker:
    # 在Docker环境中，使用MySQL数据库
    from app.models import Base
    from app.utils.database import engine
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
else:
    # 在本地环境中，使用SQLite数据库
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, declarative_base
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    # 创建数据库表
    Base.metadata.create_all(bind=engine)

# 导入API路由
from app.api import books, users, orders, carbon_points, delivery, charity, study_notes, data_analysis, support

# 导入中间件
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.middleware.replay_protection import replay_protection_middleware
from app.utils.logger import log_request_middleware
from app.utils.performance import performance_middleware

app = FastAPI(
    title="书驿云桥 API",
    description="高校图书资源共享生态平台 API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置Gzip压缩
app.add_middleware(GZipMiddleware, minimum_size=1024)

# 注册中间件
app.middleware("http")(log_request_middleware)
app.middleware("http")(performance_middleware)
app.middleware("http")(replay_protection_middleware)

# 注册路由
app.include_router(books.router, prefix="/api/books", tags=["books"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(carbon_points.router, prefix="/api/carbon-points", tags=["carbon-points"])
app.include_router(delivery.router, prefix="/api/delivery", tags=["delivery"])
app.include_router(charity.router, prefix="/api/charity", tags=["charity"])
app.include_router(study_notes.router, prefix="/api/study-notes", tags=["study-notes"])
app.include_router(data_analysis.router, prefix="/api/data-analysis", tags=["data-analysis"])
app.include_router(support.router, prefix="/api/support", tags=["support"])

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 根路径
@app.get("/")
async def root():
    return {"message": "书驿云桥 API 服务运行中"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )