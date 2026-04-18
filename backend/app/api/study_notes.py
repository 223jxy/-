from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.study_note import StudyNote
from app.models.user import User
from app.schemas.study_note import StudyNoteCreate, StudyNoteUpdate, StudyNoteResponse
from app.utils.database import get_db
from app.api.users import get_current_user

router = APIRouter()

# 创建学霸笔记
@router.post("/", response_model=StudyNoteResponse)
async def create_study_note(study_note: StudyNoteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 创建学霸笔记
    db_study_note = StudyNote(
        title=study_note.title,
        author_id=current_user.id,
        content=study_note.content,
        price=study_note.price
    )
    db.add(db_study_note)
    db.commit()
    db.refresh(db_study_note)
    return db_study_note

# 获取学霸笔记列表
@router.get("/", response_model=List[StudyNoteResponse])
async def get_study_notes(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(StudyNote)
    
    if search:
        query = query.filter(StudyNote.title.contains(search) | StudyNote.content.contains(search))
    
    study_notes = query.offset(skip).limit(limit).all()
    return study_notes

# 获取学霸笔记详情
@router.get("/{note_id}", response_model=StudyNoteResponse)
async def get_study_note(note_id: int, db: Session = Depends(get_db)):
    db_study_note = db.query(StudyNote).filter(StudyNote.id == note_id).first()
    if not db_study_note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    # 增加浏览量
    db_study_note.views += 1
    db.commit()
    
    return db_study_note

# 更新学霸笔记
@router.put("/{note_id}", response_model=StudyNoteResponse)
async def update_study_note(note_id: int, study_note: StudyNoteUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_study_note = db.query(StudyNote).filter(StudyNote.id == note_id).first()
    if not db_study_note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    # 检查是否是作者
    if db_study_note.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权更新此笔记")
    
    for key, value in study_note.dict(exclude_unset=True).items():
        setattr(db_study_note, key, value)
    
    db.commit()
    db.refresh(db_study_note)
    return db_study_note

# 删除学霸笔记
@router.delete("/{note_id}")
async def delete_study_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_study_note = db.query(StudyNote).filter(StudyNote.id == note_id).first()
    if not db_study_note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    # 检查是否是作者
    if db_study_note.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此笔记")
    
    db.delete(db_study_note)
    db.commit()
    return {"message": "笔记删除成功"}

# 购买学霸笔记
@router.post("/{note_id}/purchase")
async def purchase_study_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_study_note = db.query(StudyNote).filter(StudyNote.id == note_id).first()
    if not db_study_note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    # 检查是否是作者自己
    if db_study_note.author_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能购买自己的笔记")
    
    # 模拟购买流程
    # 实际项目中应该创建订单并处理支付
    
    # 计算作者和平台的分成（作者70%，平台30%）
    author_share = db_study_note.price * 0.7
    platform_share = db_study_note.price * 0.3
    
    print(f"用户 {current_user.username} 购买了笔记 {db_study_note.title}，价格：{db_study_note.price}")
    print(f"作者分成：{author_share}，平台分成：{platform_share}")
    
    return {"message": "购买成功", "author_share": author_share, "platform_share": platform_share}

# 点赞学霸笔记
@router.post("/{note_id}/like")
async def like_study_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_study_note = db.query(StudyNote).filter(StudyNote.id == note_id).first()
    if not db_study_note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    # 增加点赞数
    db_study_note.likes += 1
    db.commit()
    
    return {"message": "点赞成功", "likes": db_study_note.likes}