import csv
import json
import random
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

def convert_csv_to_json(csv_file_path, json_file_path, mode='dict'):
    """
    将CSV转换为JSON
    :param csv_file_path: CSV文件路径
    :param json_file_path: 输出JSON路径
    :param mode: 'list' (扁平数组) 或 'dict' (按module分组，适配你的题库结构)
    """
    
    # 用于存储结果的容器
    result_data = {} if mode == 'dict' else []

    try:
        # 打开CSV文件 (encoding='utf-8-sig' 可以处理Excel保存的CSV中的BOM字符)
        with open(csv_file_path, mode='r', encoding='utf-8-sig') as csv_file:
            # 使用 DictReader 自动将表头映射为字典key
            reader = csv.DictReader(csv_file)
            
            # 打印检测到的表头，方便调试
            print(f"检测到的CSV表头: {reader.fieldnames}")

            for row in reader:
                # 1. 处理 Tags：将字符串 "tag1,tag2" 转为列表 ["tag1", "tag2"]
                raw_tags = row.get('tags', '')
                # 替换中文逗号，去除空格，并分割
                tags_list = [t.strip() for t in raw_tags.replace('，', ',').split(',') if t.strip()]

                # 2. 构建单个问题对象
                question_item = {
                    "question": row.get('question', '').strip(),
                    "reference_answer": row.get('answer', '').strip(),
                    # 如果CSV里没有difficulty列，默认给3，或者随机1-5
                    "difficulty": int(row.get('difficulty', 3)), 
                    "category": row.get('module', '未分类'), # 使用 module 作为大类
                    "sub_category": row.get('submodule', ''), # 保留子模块信息以便参考
                    "tags": tags_list
                }

                # 3. 根据模式添加到结果中
                if mode == 'dict':
                    category_key = row.get('module', '其他')
                    if category_key not in result_data:
                        result_data[category_key] = []
                    result_data[category_key].append(question_item)
                else:
                    result_data.append(question_item)

        # 写入 JSON 文件
        with open(json_file_path, mode='w', encoding='utf-8') as json_file:
            # ensure_ascii=False 保证输出中文而不是 \uXXXX
            # indent=4 保证格式化缩进，易读
            json.dump(result_data, json_file, ensure_ascii=False, indent=4)
            
        print(f"✅ 转换成功！文件已保存至: {json_file_path}")
        print(f"共处理数据结构: {len(result_data)} 组")

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        print("请检查CSV文件编码是否为UTF-8，以及表头名称是否正确。")

# ================= 使用示例 =================

# 假设你的文件名为 data.csv，输出名为 questions.json
# 请确保你的CSV文件和脚本在同一目录下，或者填写绝对路径
input_csv = os.path.join(current_dir, 'data.csv') 
output_json = os.path.join(current_dir, 'interview_questions.json')


# 运行
if __name__ == '__main__':
    # create_sample_csv() # <--- 如果你有真实文件，请注释这一行
    
    # 执行转换
    convert_csv_to_json(input_csv, output_json, mode='dict')