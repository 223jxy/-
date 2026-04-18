from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.models.user import User
from app.schemas.support import SupportCreate, SupportUpdate, SupportResponse
from app.utils.database import get_db
from app.api.users import get_current_user

router = APIRouter()

# 模拟客服请求模型
class Support:
    def __init__(self, id, user_id, type, subject, message, status, created_at, updated_at):
        self.id = id
        self.user_id = user_id
        self.type = type
        self.subject = subject
        self.message = message
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

# 模拟客服请求数据
support_requests = [
    Support(1, 1, "投诉", "图书品相与描述不符", "我收到的图书品相明显低于描述的A1级，页面有多处破损", "待处理", datetime.utcnow(), datetime.utcnow()),
    Support(2, 2, "咨询", "短租流程", "我想了解短租图书的具体流程和注意事项", "已处理", datetime.utcnow(), datetime.utcnow())
]

# 创建客服请求
@router.post("/", response_model=SupportResponse)
async def create_support_request(support: SupportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 模拟创建客服请求
    new_request = Support(
        id=len(support_requests) + 1,
        user_id=current_user.id,
        type=support.type,
        subject=support.subject,
        message=support.message,
        status="待处理",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    support_requests.append(new_request)
    return new_request

# 获取客服请求列表
@router.get("/", response_model=List[SupportResponse])
async def get_support_requests(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    request_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 模拟获取客服请求列表
    filtered_requests = [r for r in support_requests if r.user_id == current_user.id]
    
    if status:
        filtered_requests = [r for r in filtered_requests if r.status == status]
    if request_type:
        filtered_requests = [r for r in filtered_requests if r.type == request_type]
    
    return filtered_requests[skip:skip+limit]

# 获取客服请求详情
@router.get("/{request_id}", response_model=SupportResponse)
async def get_support_request(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 模拟获取客服请求详情
    request = next((r for r in support_requests if r.id == request_id and r.user_id == current_user.id), None)
    if not request:
        raise HTTPException(status_code=404, detail="客服请求不存在")
    return request

# 更新客服请求状态
@router.put("/{request_id}", response_model=SupportResponse)
async def update_support_request(request_id: int, support: SupportUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 模拟更新客服请求状态
    request = next((r for r in support_requests if r.id == request_id and r.user_id == current_user.id), None)
    if not request:
        raise HTTPException(status_code=404, detail="客服请求不存在")
    
    if support.status:
        request.status = support.status
    request.updated_at = datetime.utcnow()
    
    return request

# 删除客服请求
@router.delete("/{request_id}")
async def delete_support_request(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 模拟删除客服请求
    global support_requests
    support_requests = [r for r in support_requests if not (r.id == request_id and r.user_id == current_user.id)]
    return {"message": "客服请求删除成功"}