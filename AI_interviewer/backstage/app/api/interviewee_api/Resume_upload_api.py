from fastapi import APIRouter, Form, UploadFile, File, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.core.get_user import get_current_user_id
from app.models.Resume_message import Resume_messages
from app.utils.qwen_client import call_vl_model_multipage
import shutil
import os
import asyncio
import uuid

router = APIRouter()

# === 后台任务处理函数 ===
async def process_and_save_resume(user_id: str, job_data: dict, file_path: str, resume_text_input: str):
    """
    后台异步处理：
    1. 调用 DeepSeek-VL2 生成/优化简历文本
    2. 存入数据库 (Upsert) - 将用户输入的文本和AI解析的文本分开存储
    """
    print(f"🔄 [Background] Start processing for User: {user_id}")
    
    # 初始化 AI 解析内容为空
    ai_parsed_content = ""
    
    # 1. 如果有文件，调用 VL 模型解析内容
    if file_path and os.path.exists(file_path):
        print(f"🤖 [Background] Calling DeepSeek-VL2 for file: {file_path}")
        try:
            # 使用 asyncio.to_thread 将同步的 API 调用放入线程池，避免阻塞事件循环
            ai_generated_text = await asyncio.to_thread(call_vl_model_multipage, file_path)
            
            if ai_generated_text and not ai_generated_text.startswith("Error"):
                # 修改点：将 API 返回的内容赋值给独立变量，不再拼接到 resume_text
                ai_parsed_content = ai_generated_text
                print("✅ [Background] AI parsing successful")
            elif ai_generated_text.startswith("Error"):
                 print(f"⚠️ [Background] AI processing returned error: {ai_generated_text}")

        except Exception as e:
            print(f"❌ [Background] AI processing failed: {e}")

    # 2. 数据库操作 (Upsert)
    async with AsyncSessionLocal() as db:
        try:
            # 检查是否存在该用户的记录
            stmt = select(Resume_messages).where(Resume_messages.user_id == user_id)
            result = await db.execute(stmt)
            existing_record = result.scalars().first()
            
            if existing_record:
                print(f"📝 [Background] Updating existing record for User: {user_id}")
                # 更新现有记录
                existing_record.job_name = job_data['job_name']
                existing_record.job_desc = job_data['job_desc']
                existing_record.company_intended = job_data['company_name']
                existing_record.company_intended_type = job_data['company_desc']
                
                # 修改点：分别存储用户输入的文本和AI解析的文件文本
                existing_record.resume_text = resume_text_input     # 用户手动粘贴的文本
                existing_record.resume_file_text = ai_parsed_content # API返回的文本 (新增字段)
                
                existing_record.resume_file_path = file_path
            else:
                print(f"🆕 [Background] Creating new record for User: {user_id}")
                # 创建新记录
                new_record = Resume_messages(
                    session_id=str(uuid.uuid4()),
                    user_id=user_id,
                    job_name=job_data['job_name'],
                    job_desc=job_data['job_desc'],
                    company_intended=job_data['company_name'],
                    company_intended_type=job_data['company_desc'],
                    
                    # 修改点：分别存储
                    resume_text=resume_text_input,      # 用户手动粘贴的文本
                    resume_file_text=ai_parsed_content, # API返回的文本 (新增字段)
                    
                    resume_file_path=file_path
                )
                db.add(new_record)
            
            await db.commit()
            print(f"✅ [Background] Data saved successfully for User: {user_id}")
            
        except Exception as e:
            print(f"❌ [Background] Database error: {e}")
            await db.rollback()

@router.post("/upload_resume")
async def create_interview_session(
    background_tasks: BackgroundTasks,
    job_name: str = Form(...),
    job_desc: str = Form(""),
    company_name: str = Form(""),
    company_desc: str = Form(""),
    resume_text: str = Form(""),
    resume_file: UploadFile = File(None),
    current_user_id: str = Depends(get_current_user_id)
):
    print(f"📥 [API] Received request from User: {current_user_id}, Job: {job_name}")

    # === 1. 立即保存文件 (主线程/IO线程) ===
    base_path = "data/resumes"
    os.makedirs(base_path, exist_ok=True)
    
    saved_file_path = ""
    if resume_file:
        file_ext = os.path.splitext(resume_file.filename)[1]
        file_name = f"{current_user_id}_{uuid.uuid4()}{file_ext}"
        saved_file_path = os.path.join(base_path, file_name)
        
        try:
            with open(saved_file_path, "wb+") as buffer:
                shutil.copyfileobj(resume_file.file, buffer)
            print(f"💾 [API] File saved to: {saved_file_path}")
        except Exception as e:
            print(f"❌ [API] File save failed: {e}")

    # === 2. 准备数据包 ===
    job_data = {
        "job_name": job_name,
        "job_desc": job_desc,
        "company_name": company_name,
        "company_desc": company_desc
    }

    # === 3. 添加后台任务 ===
    background_tasks.add_task(
        process_and_save_resume,
        user_id=current_user_id,
        job_data=job_data,
        file_path=saved_file_path,
        resume_text_input=resume_text
    )

    # === 4. 立即返回成功 ===
    return {"message": "Upload successful, processing in background", "status": "processing"}