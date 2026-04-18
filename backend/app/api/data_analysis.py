from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.models.user import User
from app.models.book import Book
from app.models.order import Order
from app.models.carbon_point import CarbonPoint
from app.models.charity import Charity
from app.models.delivery import Delivery
from app.utils.database import get_db
from app.api.users import get_current_user

router = APIRouter()

# 获取个人统计数据
@router.get("/personal")
async def get_personal_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 计算个人图书流通量
    total_books = db.query(Book).filter(Book.owner_id == current_user.id).count()
    sold_books = db.query(Book).filter(Book.owner_id == current_user.id, Book.is_sold == True).count()
    rented_books = db.query(Book).filter(Book.owner_id == current_user.id, Book.is_rented == True).count()
    
    # 计算个人订单数量
    total_orders = db.query(Order).filter(Order.user_id == current_user.id).count()
    completed_orders = db.query(Order).filter(Order.user_id == current_user.id, Order.status == "COMPLETED").count()
    
    # 计算个人碳积分
    total_carbon_points = current_user.carbon_points
    carbon_point_records = db.query(CarbonPoint).filter(CarbonPoint.user_id == current_user.id).order_by(CarbonPoint.created_at.desc()).limit(10).all()
    
    # 计算个人公益成果
    total_donations = db.query(Charity).filter(Charity.donor_id == current_user.id).count()
    total_volunteer_hours = db.query(Charity).filter(Charity.donor_id == current_user.id).all()
    volunteer_hours = sum([charity.volunteer_hours for charity in total_volunteer_hours])
    
    return {
        "books": {
            "total": total_books,
            "sold": sold_books,
            "rented": rented_books
        },
        "orders": {
            "total": total_orders,
            "completed": completed_orders
        },
        "carbon_points": {
            "total": total_carbon_points,
            "recent_records": [
                {
                    "points": record.points,
                    "source": record.source,
                    "created_at": record.created_at
                }
                for record in carbon_point_records
            ]
        },
        "charity": {
            "total_donations": total_donations,
            "volunteer_hours": volunteer_hours
        }
    }

# 获取校园统计数据
@router.get("/campus/{university}")
async def get_campus_stats(university: str, db: Session = Depends(get_db)):
    # 计算校园图书流通量
    total_books = db.query(Book).filter(Book.university == university).count()
    sold_books = db.query(Book).filter(Book.university == university, Book.is_sold == True).count()
    rented_books = db.query(Book).filter(Book.university == university, Book.is_rented == True).count()
    
    # 计算校园用户数量
    total_users = db.query(User).filter(User.university == university).count()
    
    # 计算校园碳积分总量
    users = db.query(User).filter(User.university == university).all()
    total_carbon_points = sum([user.carbon_points for user in users])
    
    # 计算校园公益成果
    total_donations = db.query(Charity).join(User).filter(User.university == university).count()
    total_volunteer_hours = db.query(Charity).join(User).filter(User.university == university).all()
    volunteer_hours = sum([charity.volunteer_hours for charity in total_volunteer_hours])
    
    return {
        "university": university,
        "books": {
            "total": total_books,
            "sold": sold_books,
            "rented": rented_books
        },
        "users": total_users,
        "carbon_points": total_carbon_points,
        "charity": {
            "total_donations": total_donations,
            "volunteer_hours": volunteer_hours
        }
    }

# 获取图书采购建议
@router.get("/recommendations")
async def get_book_recommendations(db: Session = Depends(get_db)):
    # 模拟图书采购建议
    # 实际项目中应该基于图书流通数据和需求分析生成建议
    recommendations = [
        {
            "category": "教材",
            "recommended_books": 100,
            "reason": "需求量大，流通率高"
        },
        {
            "category": "备考资料",
            "recommended_books": 50,
            "reason": "考试季节需求增加"
        },
        {
            "category": "课外读物",
            "recommended_books": 30,
            "reason": "丰富学生课余生活"
        }
    ]
    
    return recommendations

# 获取运营数据统计
@router.get("/operation")
async def get_operation_stats(db: Session = Depends(get_db)):
    # 计算总用户数量
    total_users = db.query(User).count()
    
    # 计算总图书数量
    total_books = db.query(Book).count()
    sold_books = db.query(Book).filter(Book.is_sold == True).count()
    rented_books = db.query(Book).filter(Book.is_rented == True).count()
    
    # 计算总订单数量
    total_orders = db.query(Order).count()
    completed_orders = db.query(Order).filter(Order.status == "COMPLETED").count()
    
    # 计算总碳积分
    users = db.query(User).all()
    total_carbon_points = sum([user.carbon_points for user in users])
    
    # 计算总公益成果
    total_donations = db.query(Charity).count()
    total_volunteer_hours = db.query(Charity).all()
    volunteer_hours = sum([charity.volunteer_hours for charity in total_volunteer_hours])
    
    # 计算总配送订单
    total_deliveries = db.query(Delivery).count()
    completed_deliveries = db.query(Delivery).filter(Delivery.status == "DELIVERED").count()
    
    return {
        "users": total_users,
        "books": {
            "total": total_books,
            "sold": sold_books,
            "rented": rented_books
        },
        "orders": {
            "total": total_orders,
            "completed": completed_orders
        },
        "carbon_points": total_carbon_points,
        "charity": {
            "total_donations": total_donations,
            "volunteer_hours": volunteer_hours
        },
        "deliveries": {
            "total": total_deliveries,
            "completed": completed_deliveries
        }
    }