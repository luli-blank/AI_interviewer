from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.db.session import get_db
from app.core.get_user import get_current_user_id, get_current_user_int_id
from app.models.Interview_record import Interview_record
from app.models.Interview_position import Interview_position
from app.models.Interviewer import Interviewer
from app.schemas.Interview_record import InterviewRecordCreate, InterviewRecord

router = APIRouter()

@router.post("/create_record", response_model=InterviewRecord)
async def create_record(
    record_in: InterviewRecordCreate,
    current_user_id: int = Depends(get_current_user_int_id),
    db: AsyncSession = Depends(get_db)
):
    new_record = Interview_record(
        user_id=current_user_id,
        position_id=record_in.position_id,
        interviewer_id=record_in.interviewer_id
    )
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    return new_record

@router.get("/get_records", response_model=List[InterviewRecord])
async def get_records(
    current_user_id: int = Depends(get_current_user_int_id),
    db: AsyncSession = Depends(get_db)
):
    # 查询记录并关联岗位和面试官信息
    stmt = (
        select(Interview_record, Interview_position.position_name, Interviewer.name)
        .join(Interview_position, Interview_record.position_id == Interview_position.id)
        .join(Interviewer, Interview_record.interviewer_id == Interviewer.id)
        .where(Interview_record.user_id == current_user_id)
        .order_by(desc(Interview_record.time))
    )
    
    result = await db.execute(stmt)
    records = result.all()
    
    # 构造返回数据
    response_data = []
    for record, position_name, interviewer_name in records:
        record_dict = {
            "id": record.id,
            "user_id": record.user_id,
            "position_id": record.position_id,
            "interviewer_id": record.interviewer_id,
            "time": record.time,
            "position_name": position_name,
            "interviewer_name": interviewer_name
        }
        response_data.append(record_dict)
        
    return response_data
