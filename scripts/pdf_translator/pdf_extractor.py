"""
PDF 内容提取器
将 PDF 转换为图片，提取文本和图片资源
"""
import fitz  # PyMuPDF
import base64
from pathlib import Path
from PIL import Image
import io
from .config import PDF_DPI, TEMP_DIR


def pdf_to_images(pdf_path: str, dpi: int = PDF_DPI) -> list[dict]:
    """
    将 PDF 每页转换为图片
    返回: [{"page": 0, "image_base64": "...", "image_path": "..."}]
    """
    doc = fitz.open(pdf_path)
    images = []
    
    pdf_name = Path(pdf_path).stem
    output_dir = TEMP_DIR / pdf_name
    output_dir.mkdir(exist_ok=True)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        # 转换为图片
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        
        # 保存为 PNG
        img_path = output_dir / f"page_{page_num + 1}.png"
        pix.save(str(img_path))
        
        # 转换为 base64
        img_bytes = pix.tobytes("png")
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        
        images.append({
            "page": page_num + 1,
            "image_path": str(img_path),
            "image_base64": img_base64,
            "width": pix.width,
            "height": pix.height
        })
    
    doc.close()
    return images


def extract_embedded_images(pdf_path: str) -> list[dict]:
    """
    提取 PDF 中嵌入的图片（产品图、接线图等）
    """
    doc = fitz.open(pdf_path)
    images = []
    
    pdf_name = Path(pdf_path).stem
    output_dir = TEMP_DIR / pdf_name / "embedded"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    img_count = 0
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # 过滤太小的图片（可能是装饰元素）
                pil_img = Image.open(io.BytesIO(image_bytes))
                if pil_img.width < 50 or pil_img.height < 50:
                    continue
                
                img_count += 1
                img_path = output_dir / f"img_{img_count}.{image_ext}"
                
                with open(img_path, "wb") as f:
                    f.write(image_bytes)
                
                images.append({
                    "page": page_num + 1,
                    "image_path": str(img_path),
                    "width": pil_img.width,
                    "height": pil_img.height,
                    "format": image_ext
                })
            except Exception as e:
                print(f"提取图片失败: {e}")
                continue
    
    doc.close()
    return images


def extract_text_blocks(pdf_path: str) -> list[dict]:
    """
    提取 PDF 文本块（保留位置信息）
    """
    doc = fitz.open(pdf_path)
    blocks = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text_dict = page.get_text("dict")
        
        for block in text_dict.get("blocks", []):
            if block.get("type") == 0:  # 文本块
                text = ""
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text += span.get("text", "")
                    text += "\n"
                
                if text.strip():
                    blocks.append({
                        "page": page_num + 1,
                        "text": text.strip(),
                        "bbox": block.get("bbox")
                    })
    
    doc.close()
    return blocks
