from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.order import Order, OrderStatus, OrderType
from app.models.book import Book
from app.models.user import User
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from app.utils.database import get_db
from app.api.users import get_current_user
from app.utils.performance import performance_monitor

router = APIRouter()


@router.post("/", response_model=OrderResponse, summary="创建订单")
@performance_monitor.monitor_api("create_order")
async def create_order(order: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    创建新订单
    
    - **book_id**: 图书ID
    - **order_type**: 订单类型（SALE: 购买, RENT: 出租）
    - **price**: 价格
    """
    # 检查图书是否存在
    db_book = db.query(Book).filter(Book.id == order.book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="图书不存在")
    
    # 检查图书是否已售出或出租
    if db_book.is_sold or db_book.is_rented:
        raise HTTPException(status_code=400, detail="图书已售出或出租")
    
    # 检查是否是自己的图书
    if db_book.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能购买自己的图书")
    
    # 创建订单
    db_order = Order(
        user_id=current_user.id,
        book_id=order.book_id,
        order_type=order.order_type,
        price=order.price,
        status=OrderStatus.PENDING
    )
    db.add(db_order)
    
    # 更新图书状态
    if order.order_type == OrderType.SALE:
        db_book.is_sold = True
    else:
        db_book.is_rented = True
    
    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/", response_model=List[OrderResponse], summary="获取订单列表")
@performance_monitor.monitor_api("get_orders")
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    status: OrderStatus = None,
    order_type: OrderType = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取订单列表
    
    - **skip**: 跳过条数
    - **limit**: 限制条数
    - **status**: 订单状态
    - **order_type**: 订单类型
    """
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    if status:
        query = query.filter(Order.status == status)
    if order_type:
        query = query.filter(Order.order_type == order_type)
    
    orders = query.offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse, summary="获取订单详情")
@performance_monitor.monitor_api("get_order")
async def get_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    获取订单详情
    
    - **order_id**: 订单ID
    """
    db_order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return db_order


@router.put("/{order_id}", response_model=OrderResponse, summary="更新订单状态")
@performance_monitor.monitor_api("update_order")
async def update_order(order_id: int, order: OrderUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    更新订单状态
    
    - **order_id**: 订单ID
    - **status**: 订单状态
    """
    db_order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    for key, value in order.dict(exclude_unset=True).items():
        setattr(db_order, key, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order


@router.delete("/{order_id}", summary="取消订单")
@performance_monitor.monitor_api("cancel_order")
async def cancel_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    取消订单
    
    - **order_id**: 订单ID
    """
    db_order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 只有待付款状态的订单可以取消
    if db_order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="只能取消待付款状态的订单")
    
    # 更新订单状态
    db_order.status = OrderStatus.CANCELLED
    
    # 恢复图书状态
    db_book = db.query(Book).filter(Book.id == db_order.book_id).first()
    if db_book:
        if db_order.order_type == OrderType.SALE:
            db_book.is_sold = False
        else:
            db_book.is_rented = False
    
    db.commit()
    return {"message": "订单取消成功"}