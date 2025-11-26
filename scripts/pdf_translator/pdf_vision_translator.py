"""
PDF Vision 翻译器
使用 AI Vision 识别完整段落并翻译，保持原始布局
"""
import fitz  # PyMuPDF
import json
import base64
import re
import httpx
from pathlib import Path
from typing import Optional
from .config import OUTPUT_DIR, DEFAULT_MODEL, OPENROUTER_API_KEY, OPENROUTER_BASE_URL


class PDFVisionTranslator:
    """
    使用 AI Vision 进行 PDF 翻译
    - 将 PDF 页面转为图片
    - AI 识别文本块位置和内容
    - 翻译后精准替换回原位置
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.model = model or "google/gemini-2.5-flash"  # Vision 模型
        self.base_url = OPENROUTER_BASE_URL
    
    def _pdf_page_to_image(self, page: fitz.Page, dpi: int = 150) -> bytes:
        """将 PDF 页面转换为 PNG 图片"""
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        return pix.tobytes("png")
    
    def _image_to_base64(self, image_bytes: bytes) -> str:
        """图片转 base64"""
        return base64.b64encode(image_bytes).decode("utf-8")
    
    def _call_vision_api(self, image_base64: str, page_width: float, page_height: float) -> dict:
        """
        调用 Vision API 识别并翻译页面
        返回文本块列表，每个包含：原文、译文、边界框
        """
        prompt = f"""Analyze this PDF page image and extract ALL Chinese text blocks.

PAGE SIZE: {page_width:.1f} x {page_height:.1f} points (PDF coordinates)

For each text block, provide:
1. The original Chinese text (complete paragraph/sentence, merge lines that belong together)
2. English translation (concise, similar length to Chinese)
3. Bounding box in PDF coordinates [x0, y0, x1, y1] where:
   - (x0, y0) is top-left corner
   - (x1, y1) is bottom-right corner
   - Origin (0,0) is at TOP-LEFT of page
   - x increases rightward, y increases downward

CRITICAL RULES:
- MERGE text lines that form a complete sentence/paragraph
- Keep table cells as separate blocks
- Keep titles/headers as separate blocks
- Coordinates must be in PDF points (not pixels)
- Be precise with bounding boxes

Return JSON array:
```json
[
  {{
    "chinese": "完整的中文段落文本",
    "english": "Complete English translation",
    "bbox": [x0, y0, x1, y1]
  }}
]
```

Only return the JSON array, no other text."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": 8192,
            "temperature": 0.1
        }
        
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
        
        content = result["choices"][0]["message"]["content"]
        return self._parse_vision_response(content)
    
    def _parse_vision_response(self, content: str) -> list[dict]:
        """解析 Vision API 返回的 JSON"""
        # 提取 JSON 部分
        json_match = re.search(r'\[[\s\S]*\]', content)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # 尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print(f"   警告: 无法解析 Vision 响应")
            return []
    
    def _apply_translations(self, page: fitz.Page, blocks: list[dict], dpi: int = 150):
        """
        将翻译应用到 PDF 页面
        """
        # DPI 缩放因子（图片坐标 → PDF 坐标）
        scale = 72 / dpi
        
        font = fitz.Font("helv")
        
        for block in blocks:
            chinese = block.get("chinese", "")
            english = block.get("english", "")
            bbox = block.get("bbox", [])
            
            if not english or len(bbox) != 4:
                continue
            
            # 坐标转换（如果 AI 返回的是像素坐标，需要缩放）
            x0, y0, x1, y1 = bbox
            
            # 检查坐标是否合理（如果太大，可能是像素坐标）
            page_rect = page.rect
            if x1 > page_rect.width * 1.5 or y1 > page_rect.height * 1.5:
                # 可能是像素坐标，需要缩放
                x0, y0, x1, y1 = x0 * scale, y0 * scale, x1 * scale, y1 * scale
            
            rect = fitz.Rect(x0, y0, x1, y1)
            
            # 确保矩形在页面范围内
            rect = rect & page.rect
            if rect.is_empty:
                continue
            
            # 白色覆盖原文
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
            
            # 计算合适的字体大小
            rect_height = rect.height
            rect_width = rect.width
            
            # 估算字体大小（基于区域高度和文本行数）
            line_count = english.count('\n') + 1
            base_size = min(rect_height / line_count * 0.8, 12)
            
            # 测量文本宽度，调整字体大小
            text_width = font.text_length(english.replace('\n', ' '), fontsize=base_size)
            if text_width > rect_width:
                base_size = base_size * (rect_width / text_width) * 0.95
            
            font_size = max(base_size, 5)  # 最小 5pt
            
            # 插入翻译文本
            try:
                # 使用 insert_textbox 自动换行
                page.insert_textbox(
                    rect,
                    english,
                    fontsize=font_size,
                    fontname="helv",
                    color=(0, 0, 0),
                    align=fitz.TEXT_ALIGN_LEFT
                )
            except Exception as e:
                # 备用方案：直接插入
                try:
                    page.insert_text(
                        (rect.x0, rect.y0 + font_size),
                        english,
                        fontsize=font_size,
                        fontname="helv",
                        color=(0, 0, 0)
                    )
                except:
                    print(f"   警告: 无法插入文本 '{english[:30]}...'")
    
    def translate_pdf(
        self, 
        input_path: str, 
        output_path: str = None,
        dpi: int = 150,
        pages: list[int] = None
    ) -> str:
        """
        使用 Vision AI 翻译 PDF
        
        Args:
            input_path: 输入 PDF 路径
            output_path: 输出 PDF 路径
            dpi: 图片 DPI（越高越精确，但更慢）
            pages: 要翻译的页码列表（从0开始），None 表示全部
        
        Returns:
            输出文件路径
        """
        input_path = Path(input_path)
        if output_path is None:
            output_path = OUTPUT_DIR / f"{input_path.stem}_EN_vision.pdf"
        
        print(f"📄 开始 Vision 翻译: {input_path.name}")
        print(f"   使用模型: {self.model}")
        print(f"   DPI: {dpi}")
        
        doc = fitz.open(str(input_path))
        total_pages = len(doc)
        
        if pages is None:
            pages = list(range(total_pages))
        
        print(f"   总页数: {total_pages}, 翻译页数: {len(pages)}")
        
        for page_num in pages:
            if page_num >= total_pages:
                continue
                
            page = doc[page_num]
            print(f"\n📖 处理第 {page_num + 1}/{total_pages} 页...")
            
            # 转换为图片
            image_bytes = self._pdf_page_to_image(page, dpi=dpi)
            image_base64 = self._image_to_base64(image_bytes)
            
            # 调用 Vision API
            print(f"   🤖 AI 识别中...")
            blocks = self._call_vision_api(
                image_base64, 
                page.rect.width, 
                page.rect.height
            )
            print(f"   找到 {len(blocks)} 个文本块")
            
            # 应用翻译
            if blocks:
                self._apply_translations(page, blocks, dpi=dpi)
                print(f"   ✅ 翻译完成")
        
        # 保存
        print(f"\n💾 保存文件...")
        doc.save(str(output_path))
        doc.close()
        
        print(f"✅ 完成! 输出: {output_path}")
        return str(output_path)


def translate_pdf_vision(
    pdf_path: str,
    api_key: str = None,
    model: str = None,
    output_path: str = None,
    dpi: int = 150,
    pages: list[int] = None
) -> str:
    """
    便捷函数：使用 Vision AI 翻译 PDF
    """
    translator = PDFVisionTranslator(api_key=api_key, model=model)
    return translator.translate_pdf(pdf_path, output_path, dpi=dpi, pages=pages)
