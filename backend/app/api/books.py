from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List
import shutil
import os

from app.models.book import Book, BookCondition
from app.models.user import User
from app.schemas.book import BookCreate, BookUpdate, BookResponse
from app.utils.database import get_db
from app.utils.pricing import calculate_price, validate_price
from app.utils.redis import RedisCache, CACHE_PREFIX
from app.utils.rate_limit import rate_limit
from app.utils.circuit_breaker import CircuitBreaker
from app.utils.input_validation import InputValidator, VALIDATION_RULES
from app.api.users import get_current_user
from app.utils.performance import performance_monitor

router = APIRouter()


@router.post("/", response_model=BookResponse, summary="创建图书")
@performance_monitor.monitor_api("create_book")
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """
    创建新图书
    
    - **title**: 图书标题
    - **author**: 作者
    - **isbn**: ISBN编号
    - **original_price**: 原价
    - **condition**: 品相等级（A1/A2/B/C）
    - **category**: 分类
    - **description**: 描述
    - **university**: 学校
    - **major**: 专业
    - **grade**: 年级
    - **owner_id**: 所有者ID
    """
    # 验证输入
    book_data = book.dict()
    errors = InputValidator.validate_input(book_data, VALIDATION_RULES["book"])
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    
    # 自动计算价格
    calculated_price = calculate_price(book.original_price, book.condition, book.category)
    
    # 创建图书对象
    db_book = Book(
        **book_data,
        price=calculated_price
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    # 清除图书列表缓存
    RedisCache.delete_pattern(f"{CACHE_PREFIX['books_list']}*")
    
    return db_book


@router.post("/upload-cover/{book_id}", summary="上传图书封面")
async def upload_cover(book_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    上传图书封面
    
    - **book_id**: 图书ID
    - **file**: 封面图片文件
    """
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="图书不存在")
    
    # 确保上传目录存在
    os.makedirs("uploads/books", exist_ok=True)
    
    # 保存文件
    file_path = f"uploads/books/{book_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 更新图书封面路径
    db_book.cover_image = file_path
    db.commit()
    
    return {"message": "封面上传成功", "file_path": file_path}


@router.get("/", response_model=List[BookResponse], summary="获取图书列表")
@performance_monitor.monitor_api("get_books")
async def get_books(
    skip: int = 0,
    limit: int = 100,
    university: str = None,
    major: str = None,
    grade: str = None,
    category: str = None,
    condition: BookCondition = None,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit("books"))
):
    """
    获取图书列表
    
    - **skip**: 跳过条数
    - **limit**: 限制条数
    - **university**: 学校
    - **major**: 专业
    - **grade**: 年级
    - **category**: 分类
    - **condition**: 品相等级
    """
    @CircuitBreaker("books:get_books")
    async def get_books_inner():
        # 生成缓存键
        cache_key = f"{CACHE_PREFIX['books_list']}{skip}:{limit}:{university or ''}:{major or ''}:{grade or ''}:{category or ''}:{condition or ''}"
        
        # 尝试从缓存获取
        cached_books = RedisCache.get(cache_key)
        if cached_books:
            return cached_books
        
        # 从数据库查询
        query = db.query(Book).filter(Book.is_sold == False, Book.is_rented == False)
        
        if university:
            query = query.filter(Book.university == university)
        if major:
            query = query.filter(Book.major == major)
        if grade:
            query = query.filter(Book.grade == grade)
        if category:
            query = query.filter(Book.category == category)
        if condition:
            query = query.filter(Book.condition == condition)
        
        books = query.offset(skip).limit(limit).all()
        
        # 转换为响应模型
        book_responses = [
            BookResponse(
                id=book.id,
                title=book.title,
                author=book.author,
                isbn=book.isbn,
                price=book.price,
                original_price=book.original_price,
                condition=book.condition,
                category=book.category,
                description=book.description,
                cover_image=book.cover_image,
                university=book.university,
                major=book.major,
                grade=book.grade,
                owner_id=book.owner_id,
                is_sold=book.is_sold,
                is_rented=book.is_rented,
                created_at=book.created_at
            )
            for book in books
        ]
        
        # 缓存结果
        RedisCache.set(cache_key, [book.dict() for book in book_responses], expire=1800)  # 30分钟缓存
        
        return book_responses
    
    return await get_books_inner()


@router.get("/{book_id}", response_model=BookResponse, summary="获取图书详情")
@performance_monitor.monitor_api("get_book")
async def get_book(
    book_id: int, 
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit("books"))
):
    """
    获取图书详情
    
    - **book_id**: 图书ID
    """
    @CircuitBreaker("books:get_book")
    async def get_book_inner():
        # 生成缓存键
        cache_key = f"{CACHE_PREFIX['book']}{book_id}"
        
        # 尝试从缓存获取
        cached_book = RedisCache.get(cache_key)
        if cached_book:
            return cached_book
        
        # 从数据库查询
        db_book = db.query(Book).filter(Book.id == book_id).first()
        if not db_book:
            raise HTTPException(status_code=404, detail="图书不存在")
        
        # 转换为响应模型
        book_response = BookResponse(
            id=db_book.id,
            title=db_book.title,
            author=db_book.author,
            isbn=db_book.isbn,
            price=db_book.price,
            original_price=db_book.original_price,
            condition=db_book.condition,
            category=db_book.category,
            description=db_book.description,
            cover_image=db_book.cover_image,
            university=db_book.university,
            major=db_book.major,
            grade=db_book.grade,
            owner_id=db_book.owner_id,
            is_sold=db_book.is_sold,
            is_rented=db_book.is_rented,
            created_at=db_book.created_at
        )
        
        # 缓存结果
        RedisCache.set(cache_key, book_response.dict(), expire=3600)  # 1小时缓存
        
        return book_response
    
    return await get_book_inner()


@router.put("/{book_id}", response_model=BookResponse, summary="更新图书信息")
@performance_monitor.monitor_api("update_book")
async def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    更新图书信息
    
    - **book_id**: 图书ID
    - **title**: 图书标题
    - **author**: 作者
    - **isbn**: ISBN编号
    - **price**: 价格
    - **original_price**: 原价
    - **condition**: 品相等级
    - **category**: 分类
    - **description**: 描述
    - **is_sold**: 是否已售出
    - **is_rented**: 是否已出租
    """
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="图书不存在")
    
    # 越权操作检测：只有图书的所有者才能更新图书
    if db_book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限更新此图书")
    
    # 验证价格是否合理
    if book.price is not None:
        is_valid, min_price, max_price = validate_price(
            book.price, 
            book.original_price or db_book.original_price, 
            book.condition or db_book.condition, 
            db_book.category
        )
        if not is_valid:
            raise HTTPException(
                status_code=400, 
                detail=f"价格不合理，合理范围：{min_price} - {max_price}"
            )
    
    # 如果更新了影响价格的字段，重新计算价格
    if book.original_price is not None or book.condition is not None:
        new_price = calculate_price(
            book.original_price or db_book.original_price, 
            book.condition or db_book.condition, 
            db_book.category
        )
        book.price = new_price
    
    for key, value in book.dict(exclude_unset=True).items():
        setattr(db_book, key, value)
    
    db.commit()
    db.refresh(db_book)
    
    # 清除图书详情缓存
    RedisCache.delete(f"{CACHE_PREFIX['book']}{book_id}")
    # 清除图书列表缓存
    RedisCache.delete_pattern(f"{CACHE_PREFIX['books_list']}*")
    
    return db_book


@router.delete("/{book_id}", summary="删除图书")
@performance_monitor.monitor_api("delete_book")
async def delete_book(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    删除图书
    
    - **book_id**: 图书ID
    """
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="图书不存在")
    
    # 越权操作检测：只有图书的所有者才能删除图书
    if db_book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限删除此图书")
    
    db.delete(db_book)
    db.commit()
    
    # 清除图书详情缓存
    RedisCache.delete(f"{CACHE_PREFIX['book']}{book_id}")
    # 清除图书列表缓存
    RedisCache.delete_pattern(f"{CACHE_PREFIX['books_list']}*")
    
    return {"message": "图书删除成功"}