from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.charity import Charity
from app.models.user import User
from app.models.book import Book
from app.schemas.charity import CharityCreate, CharityUpdate, CharityResponse
from app.utils.database import get_db
from app.api.users import get_current_user

router = APIRouter()

# 创建捐赠记录
@router.post("/", response_model=CharityResponse)
async def create_charity(charity: CharityCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 检查图书是否存在
    if charity.book_id:
        db_book = db.query(Book).filter(Book.id == charity.book_id).first()
        if not db_book:
            raise HTTPException(status_code=404, detail="图书不存在")
        
        # 检查图书是否属于当前用户
        if db_book.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权捐赠此图书")
    
    # 创建捐赠记录
    db_charity = Charity(
        donor_id=current_user.id,
        book_id=charity.book_id,
        book_title=charity.book_title,
        quantity=charity.quantity,
        destination=charity.destination,
        volunteer_hours=charity.volunteer_hours
    )
    db.add(db_charity)
    
    # 如果捐赠的是平台内的图书，更新图书状态
    if charity.book_id:
        db_book = db.query(Book).filter(Book.id == charity.book_id).first()
        db_book.is_sold = True  # 标记为已售出（实际是捐赠）
    
    # 增加用户碳积分（1本书=10碳积分）
    current_user.carbon_points += charity.quantity * 10
    
    db.commit()
    db.refresh(db_charity)
    return db_charity

# 获取捐赠记录列表
@router.get("/", response_model=List[CharityResponse])
async def get_charities(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Charity).filter(Charity.donor_id == current_user.id)
    
    if status:
        query = query.filter(Charity.status == status)
    
    charities = query.offset(skip).limit(limit).all()
    return charities

# 获取捐赠记录详情
@router.get("/{charity_id}", response_model=CharityResponse)
async def get_charity(charity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_charity = db.query(Charity).filter(Charity.id == charity_id, Charity.donor_id == current_user.id).first()
    if not db_charity:
        raise HTTPException(status_code=404, detail="捐赠记录不存在")
    return db_charity

# 更新捐赠记录状态
@router.put("/{charity_id}", response_model=CharityResponse)
async def update_charity(charity_id: int, charity: CharityUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_charity = db.query(Charity).filter(Charity.id == charity_id, Charity.donor_id == current_user.id).first()
    if not db_charity:
        raise HTTPException(status_code=404, detail="捐赠记录不存在")
    
    for key, value in charity.dict(exclude_unset=True).items():
        setattr(db_charity, key, value)
    
    db.commit()
    db.refresh(db_charity)
    return db_charity

# 获取公益合伙人状态
@router.get("/partner/status")
async def get_partner_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 计算用户累计捐赠的图书数量
    total_books = db.query(Charity).filter(Charity.donor_id == current_user.id).count()
    
    # 判断是否达到公益合伙人标准（累计捐赠50本书）
    is_partner = total_books >= 50
    
    return {
        "total_books": total_books,
        "is_partner": is_partner,
        "remaining_books": max(0, 50 - total_books)
    }

# 线上支教报名
@router.post("/volunteer/teach")
async def volunteer_teach(volunteer_data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 模拟线上支教报名
    print(f"用户 {current_user.username} 报名线上支教，课程：{volunteer_data.get('course', '')}")
    
    # 增加用户志愿时长
    volunteer_hours = volunteer_data.get('hours', 0)
    
    # 创建捐赠记录（用于记录志愿时长）
    db_charity = Charity(
        donor_id=current_user.id,
        book_title="线上支教",
        quantity=0,
        destination="乡村小学",
        status="COMPLETED",
        volunteer_hours=volunteer_hours
    )
    db.add(db_charity)
    db.commit()
    
    return {"message": "线上支教报名成功", "volunteer_hours": volunteer_hours}