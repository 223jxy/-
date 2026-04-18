from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.models.delivery import Delivery, DeliveryStatus
from app.models.order import Order
from app.models.user import User
from app.schemas.delivery import DeliveryCreate, DeliveryUpdate, DeliveryResponse
from app.utils.database import get_db
from app.api.users import get_current_user

router = APIRouter()

# 创建配送订单
@router.post("/", response_model=DeliveryResponse)
async def create_delivery(delivery: DeliveryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 检查订单是否存在
    db_order = db.query(Order).filter(Order.id == delivery.order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 检查订单是否属于当前用户
    if db_order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此订单")
    
    # 检查订单是否已经有配送
    if db_order.delivery_id:
        raise HTTPException(status_code=400, detail="订单已经有配送")
    
    # 计算预计送达时间
    estimated_time = datetime.utcnow() + timedelta(hours=24)  # 默认为24小时内送达
    if delivery.is_express:
        estimated_time = datetime.utcnow() + timedelta(hours=4)  # 加急配送4小时内送达
    
    # 创建配送订单
    db_delivery = Delivery(
        order_id=delivery.order_id,
        pickup_location=delivery.pickup_location,
        delivery_location=delivery.delivery_location,
        estimated_time=estimated_time,
        fee=delivery.fee,
        reward=delivery.reward
    )
    db.add(db_delivery)
    
    # 更新订单状态
    db_order.status = "DELIVERING"
    db_order.delivery_id = db_delivery.id
    
    db.commit()
    db.refresh(db_delivery)
    return db_delivery

# 获取配送订单列表
@router.get("/", response_model=List[DeliveryResponse])
async def get_deliveries(
    skip: int = 0,
    limit: int = 100,
    status: DeliveryStatus = None,
    is_delivery_person: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if is_delivery_person:
        # 配送员查看分配给自己的配送
        query = db.query(Delivery).filter(Delivery.delivery_person_id == current_user.id)
    else:
        # 用户查看自己的配送
        query = db.query(Delivery).join(Order).filter(Order.user_id == current_user.id)
    
    if status:
        query = query.filter(Delivery.status == status)
    
    deliveries = query.offset(skip).limit(limit).all()
    return deliveries

# 获取配送订单详情
@router.get("/{delivery_id}", response_model=DeliveryResponse)
async def get_delivery(delivery_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 检查配送是否存在
    db_delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_delivery:
        raise HTTPException(status_code=404, detail="配送不存在")
    
    # 检查是否是用户自己的配送或配送员
    db_order = db.query(Order).filter(Order.id == db_delivery.order_id).first()
    if db_order.user_id != current_user.id and db_delivery.delivery_person_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此配送")
    
    return db_delivery

# 分配配送员
@router.put("/{delivery_id}/assign")
async def assign_delivery(delivery_id: int, delivery_person_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 检查配送是否存在
    db_delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_delivery:
        raise HTTPException(status_code=404, detail="配送不存在")
    
    # 检查配送员是否存在
    db_delivery_person = db.query(User).filter(User.id == delivery_person_id, User.is_delivery == True).first()
    if not db_delivery_person:
        raise HTTPException(status_code=404, detail="配送员不存在")
    
    # 分配配送员
    db_delivery.delivery_person_id = delivery_person_id
    db_delivery.status = DeliveryStatus.ASSIGNED
    
    db.commit()
    db.refresh(db_delivery)
    return db_delivery

# 更新配送状态
@router.put("/{delivery_id}", response_model=DeliveryResponse)
async def update_delivery(delivery_id: int, delivery: DeliveryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 检查配送是否存在
    db_delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_delivery:
        raise HTTPException(status_code=404, detail="配送不存在")
    
    # 检查是否是配送员
    if db_delivery.delivery_person_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有配送员可以更新配送状态")
    
    # 更新配送状态
    if delivery.status:
        db_delivery.status = delivery.status
        
        # 如果配送完成，更新订单状态
        if delivery.status == DeliveryStatus.DELIVERED:
            db_order = db.query(Order).filter(Order.id == db_delivery.order_id).first()
            if db_order:
                db_order.status = "COMPLETED"
    
    if delivery.rating:
        db_delivery.rating = delivery.rating
    
    db_delivery.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_delivery)
    return db_delivery

# 取消配送
@router.delete("/{delivery_id}")
async def cancel_delivery(delivery_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 检查配送是否存在
    db_delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_delivery:
        raise HTTPException(status_code=404, detail="配送不存在")
    
    # 检查是否是用户自己的配送
    db_order = db.query(Order).filter(Order.id == db_delivery.order_id).first()
    if db_order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权取消此配送")
    
    # 只有待分配状态的配送可以取消
    if db_delivery.status != DeliveryStatus.PENDING:
        raise HTTPException(status_code=400, detail="只能取消待分配状态的配送")
    
    # 更新配送状态
    db_delivery.status = DeliveryStatus.CANCELLED
    
    # 更新订单状态
    db_order.status = "PENDING"
    db_order.delivery_id = None
    
    db.commit()
    return {"message": "配送取消成功"}