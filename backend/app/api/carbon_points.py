from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.user import User
from app.models.carbon_point import CarbonPoint
from app.schemas.carbon_point import CarbonPointCreate, CarbonPointResponse
from app.utils.database import get_db
from app.api.users import get_current_user

router = APIRouter()

# 增加碳积分
@router.post("/", response_model=CarbonPointResponse)
async def add_carbon_points(carbon_point: CarbonPointCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 创建碳积分记录
    db_carbon_point = CarbonPoint(
        user_id=current_user.id,
        points=carbon_point.points,
        source=carbon_point.source
    )
    db.add(db_carbon_point)
    
    # 更新用户碳积分
    current_user.carbon_points += carbon_point.points
    
    db.commit()
    db.refresh(db_carbon_point)
    return db_carbon_point

# 获取用户碳积分记录
@router.get("/", response_model=List[CarbonPointResponse])
async def get_carbon_points(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    carbon_points = db.query(CarbonPoint).filter(CarbonPoint.user_id == current_user.id).offset(skip).limit(limit).all()
    return carbon_points

# 获取用户当前碳积分
@router.get("/current")
async def get_current_carbon_points(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"carbon_points": current_user.carbon_points}

# 兑换碳积分
@router.post("/redeem")
async def redeem_carbon_points(redeem_data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    points = redeem_data.get("points", 0)
    reward = redeem_data.get("reward", "")
    
    # 检查碳积分是否足够
    if current_user.carbon_points < points:
        raise HTTPException(status_code=400, detail="碳积分不足")
    
    # 扣除碳积分
    current_user.carbon_points -= points
    
    # 记录兑换记录（实际项目中应该创建兑换记录模型）
    print(f"用户 {current_user.username} 兑换了 {points} 碳积分，获得奖励：{reward}")
    
    db.commit()
    return {"message": "兑换成功", "remaining_points": current_user.carbon_points}