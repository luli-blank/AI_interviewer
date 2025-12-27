import os
import base64
import mimetypes
import io
from openai import OpenAI
import fitz  # PyMuPDF，用于替代 pdf2image，不需要系统级依赖
from app.core.config import settings

# === 1. 辅助函数：普通图片文件转 Base64 ===
def encode_file_to_base64(file_path):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# === 2. 主调用函数 ===
def call_vl_model_multipage(file_path: str, prompt: str = None) -> str:
    """
    调用多模态模型解析简历文件（支持图片和PDF）
    使用 PyMuPDF 进行 PDF 渲染，无需 sudo 权限。
    """
    # 默认提示词
    if prompt is None:
        prompt = """
        请仔细阅读这份简历图片，提取并整理简历中存在的文本信息，按照简历中的顺序进行文本转录。（不要改变简历中的文本）
        如果简历包含多页，请整合所有页面的信息。
        **注意**
        - 只需提取文本内容，不要添加任何额外信息。
        - 保持顺序，确保信息完整。
        - 格式清晰，分行。纯文本的形式返回，**禁止markdown格式**。
        """

    try:
        api_key =settings.Silicon_OCR_API_Key
        if not api_key:
            return "Error: Silicon_OCR_API_Key not found."

        # 初始化客户端
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1" 
        )

        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"

        # 准备消息内容列表
        content_parts = [
            {"type": "text", "text": prompt}
        ]

        mime_type, _ = mimetypes.guess_type(file_path)

        # === 分支 A: 处理 PDF (多页) - 使用 PyMuPDF ===
        if mime_type == 'application/pdf':
            print("正在处理多页 PDF (PyMuPDF)...")
            try:
                # 1. 打开 PDF 文档
                doc = fitz.open(file_path)
                
                # 设置最大页数防止 Token 溢出
                max_pages = 5 
                total_pages = len(doc)
                
                if total_pages > max_pages:
                    print(f"提示: PDF 页数 ({total_pages}) 超过限制，只处理前 {max_pages} 页。")
                
                # 2. 循环处理每一页
                for i in range(min(total_pages, max_pages)):
                    print(f"正在编码第 {i+1} 页...")
                    page = doc.load_page(i)
                    
                    # matrix=fitz.Matrix(2, 2) 表示放大 2 倍，提高清晰度以利于 OCR
                    # alpha=False 强制白色背景（防止透明背景变黑）
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                    
                    # 直接获取 JPEG 格式的二进制数据
                    img_bytes = pix.tobytes("jpeg")
                    
                    # 转 Base64
                    base64_img = base64.b64encode(img_bytes).decode('utf-8')
                    
                    # 3. 添加到 content 列表
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_img}"
                        }
                    })
                
                doc.close()

            except Exception as e:
                return f"PDF 转换错误: {str(e)}"

        # === 分支 B: 处理单张图片 ===
        elif mime_type and mime_type.startswith('image'):
            base64_img = encode_file_to_base64(file_path)
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_img}"
                }
            })
        
        else:
            return "Error: Unsupported file type. Only PDF, JPG, PNG supported."

        # === 4. 发送请求 ===
        print(f"发送请求中，包含 {len(content_parts)-1} 张图片...")
        
        completion = client.chat.completions.create(
            model="Qwen/Qwen3-VL-235B-A22B-Thinking", 
            messages=[
                {
                    "role": "user",
                    "content": content_parts 
                }
            ],
            max_tokens=2048 
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"API Error: {e}")
        return f"Error processing resume: {str(e)}"