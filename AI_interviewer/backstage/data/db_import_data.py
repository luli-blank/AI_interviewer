import sys
import os
import asyncio
import pandas as pd
from app.db.session import AsyncSessionLocal
from app.models.Character_question import Character_question

# 1. 路径设置
sys.path.append(os.getcwd())

# Excel 文件路径 (注意：字符串前加了 'r' 防止路径转义错误)
EXCEL_FILE_PATH = "C:/Users/23516/Desktop/1.xlsx"

async def import_data():
    if not os.path.exists(EXCEL_FILE_PATH):
        print(f"❌ 未找到文件: {EXCEL_FILE_PATH}，请确认路径是否正确。")
        return

    # =======================================================
    # 主要修改点：从读取 CSV 改为读取 Excel
    # =======================================================
    print("📖 正在读取 Excel 文件...")
    try:
        # 使用 pd.read_excel() 读取 .xlsx 文件，不再需要处理编码问题
        df = pd.read_excel(EXCEL_FILE_PATH)
    except Exception as e:
        print(f"❌ 读取 Excel 文件失败: {e}")
        return
    # =======================================================

    # 3. 列名清洗（关键步骤）
    # 为了防止表头里的括号、空格导致读取失败，我们重命名关键列
    rename_map = {}
    for col in df.columns:
        if "类别" in col: rename_map[col] = "type"
        elif "问题" in col: rename_map[col] = "questions"
        elif "选项 A" in col or "选项A" in col: rename_map[col] = "option_a"
        elif "选项 B" in col or "选项B" in col: rename_map[col] = "option_b"
        elif "选项 C" in col or "选项C" in col: rename_map[col] = "option_c"
        elif "选项 D" in col or "选项D" in col: rename_map[col] = "option_d"
    
    df.rename(columns=rename_map, inplace=True)
    
    # 检查是否所有必要的列都找到了
    required_cols = ['type', 'questions', 'option_a', 'option_b', 'option_c', 'option_d']
    if not all(col in df.columns for col in required_cols):
        print(f"❌ 列名匹配失败。检测到的列: {df.columns.tolist()}")
        print(f"   需要包含: 类别, 问题描述, 选项 A, 选项 B, 选项 C, 选项 D")
        return

    print("🚀 开始转换数据并写入数据库...")
    
    async with AsyncSessionLocal() as session:
        success_count = 0
        question_obj = None # 提前定义，防止在无数据时报错
        
        for index, row in df.iterrows():
            try:
                # 4. 数据转换逻辑 (核心部分)
                formatted_answers = [
                    {"label": str(row['option_a']).strip(), "value": "A"},
                    {"label": str(row['option_b']).strip(), "value": "B"},
                    {"label": str(row['option_c']).strip(), "value": "C"},
                    {"label": str(row['option_d']).strip(), "value": "D"}
                ]

                # 5. 构建数据库模型对象
                question_obj = Character_question(
                    type=str(row['type']).strip(),
                    questions=str(row['questions']).strip(),
                    answers=formatted_answers 
                )
                
                session.add(question_obj)
                success_count += 1
                
            except Exception as e:
                print(f"⚠️ 第 {index+1} 行处理出错: {e}")

        # 6. 提交事务
        if success_count > 0:
            try:
                await session.commit()
                print("------------------------------------------------")
                print(f"🎉 成功导入 {success_count} 条题目！")
                
                if question_obj:
                    # 验证一下最后一条数据
                    print("\n🔍 数据样例 (最后一条):")
                    print(f"Type: {question_obj.type}")
                    print(f"Question: {question_obj.questions}")
                    print(f"Answers (JSON): {question_obj.answers}")
            
            except Exception as e:
                await session.rollback()
                print(f"❌ 数据库提交失败: {e}")
        else:
            print("没有可导入的数据。")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(import_data())