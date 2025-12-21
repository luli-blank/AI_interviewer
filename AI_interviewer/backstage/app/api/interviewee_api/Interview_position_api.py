from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func  # 引入 select 用于查询, func 用于数据库函数

# 引入你的 Pydantic 模型 (schemas)
from app.schemas.Interview_position import Position, PositionWithInterviewers
# 引入你的 ORM 模型 (models)
from app.models.Interview_position import Interview_position
from app.models.Jobs import Jobs
from app.models.Interviewer import Interviewer
# 引入数据库会话依赖
from app.db.session import get_db
from app.core.get_user import get_current_user_id 
from typing import List


router = APIRouter()

@router.get("/get_position", response_model=List[PositionWithInterviewers])
async def get_position(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Interview_position))
    positions = result.scalars().all() 
    
    positions_with_interviewers = []
    for pos in positions:
        # Fetch interviewers for this position via Jobs table
        stmt = (
            select(Interviewer)
            .join(Jobs, Jobs.interviewer_id == Interviewer.id)
            .where(Jobs.position_id == pos.id)
        )
        result_interviewers = await db.execute(stmt)
        interviewers = result_interviewers.scalars().all()
        
        positions_with_interviewers.append({
            "id": pos.id,
            "position_name": pos.position_name,
            "description": pos.description,
            "interviewers": interviewers
        })
        
    return positions_with_interviewers

