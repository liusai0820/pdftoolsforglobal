"""
PDF 原位翻译器
保留原始 PDF 布局，只翻译文字内容
"""
import fitz  # PyMuPDF
import json
import re
from pathlib import Path
from typing import Optional
from .config import OUTPUT_DIR, DEFAULT_MODEL
from .ai_processor import AIProcessor


class PDFInplaceTranslator:
    """
    保留 PDF 原始布局，直接翻译文字
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        self.ai = AIProcessor(api_key=api_key, model=model)
    
    def extract_text_blocks(self, pdf_path: str) -> list[dict]:
        """
        提取所有文本块及其位置信息
        策略：按 line 级别提取，自动合并同一行内的所有 span
        """
        doc = fitz.open(pdf_path)
        all_blocks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
            
            for block in blocks:
                if block.get("type") == 0:  # 文本块
                    for line in block.get("lines", []):
                        # 收集该行所有包含中文的 span
                        chinese_spans = []
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if text and self._contains_chinese(text):
                                chinese_spans.append(span)
                        
                        # 如果该行有中文内容，合并整行
                        if chinese_spans:
                            # 合并该行所有中文 span
                            merged_text = " ".join([s.get("text", "").strip() for s in chinese_spans])
                            
                            # 计算整行的边界框
                            x0 = min(s["bbox"][0] for s in chinese_spans)
                            y0 = min(s["bbox"][1] for s in chinese_spans)
                            x1 = max(s["bbox"][2] for s in chinese_spans)
                            y1 = max(s["bbox"][3] for s in chinese_spans)
                            
                            # 使用第一个 span 的属性
                            first_span = chinese_spans[0]
                            
                            all_blocks.append({
                                "page": page_num,
                                "text": merged_text,
                                "bbox": (x0, y0, x1, y1),
                                "font": first_span.get("font"),
                                "size": first_span.get("size"),
                                "color": first_span.get("color"),
                                "origin": first_span.get("origin"),
                                "span_count": len(chinese_spans)
                            })
        
        doc.close()
        return all_blocks
    

    
    def _contains_chinese(self, text: str) -> bool:
        """检查文本是否包含中文"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))
    
    def _parse_fallback(self, response: str, original_texts: list[str]) -> dict[str, str]:
        """备用解析方案：尝试从响应中提取翻译对"""
        result = {}
        lines = response.split("\n")
        
        for text in original_texts:
            # 在响应中查找这个文本的翻译
            for line in lines:
                if text in line and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        translation = parts[1].strip().strip('"').strip("'").strip(",")
                        if translation and not self._contains_chinese(translation):
                            result[text] = translation
                            break
        
        return result
    
    def batch_translate(self, texts: list[str]) -> dict[str, str]:
        """批量翻译文本"""
        if not texts:
            return {}
        
        # 去重
        unique_texts = list(set(texts))
        
        # 分批处理（每批最多 50 条）
        batch_size = 50
        translations = {}
        
        for i in range(0, len(unique_texts), batch_size):
            batch = unique_texts[i:i + batch_size]
            batch_translations = self._translate_batch(batch)
            translations.update(batch_translations)
            print(f"   翻译进度: {min(i + batch_size, len(unique_texts))}/{len(unique_texts)}")
        
        return translations
    
    def _translate_batch(self, texts: list[str]) -> dict[str, str]:
        """翻译一批文本 - 生成简洁的英文，长度尽量接近原文"""
        # 计算每个文本的目标长度（字符数）
        text_with_limits = []
        for i, t in enumerate(texts):
            # 中文字符数 * 1.2 = 目标英文字符数上限
            max_chars = int(len(t) * 1.5)
            text_with_limits.append(f"{i+1}|||{t}|||MAX:{max_chars}chars")
        
        text_list = "\n".join(text_with_limits)
        
        prompt = f"""Translate Chinese to English for industrial sensor document.

CRITICAL RULES:
- Keep translation SHORT and CONCISE
- English length must be close to or shorter than Chinese length
- Use abbreviations where appropriate (e.g., "temp" for "temperature")
- Omit unnecessary words
- Format: NUMBER|||ENGLISH_TRANSLATION

Input:
{text_list}

Output (same NUMBER|||TRANSLATION format):"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self.ai._call_api(messages, max_tokens=8192)
        
        # 解析响应
        result = {}
        lines = response.strip().split("\n")
        
        for line in lines:
            if "|||" in line:
                parts = line.split("|||", 1)
                if len(parts) == 2:
                    try:
                        idx = int(parts[0].strip()) - 1
                        if 0 <= idx < len(texts):
                            translation = parts[1].strip()
                            # 清理翻译结果：移除可能残留的格式标记
                            translation = translation.split("|||")[0].strip()
                            # 移除 MAX: 等标记
                            if "MAX:" in translation:
                                translation = translation.split("MAX:")[0].strip()
                            if translation:
                                result[texts[idx]] = translation
                    except ValueError:
                        continue
        
        return result
    


    def translate_pdf(
        self, 
        input_path: str, 
        output_path: str = None,
        font_path: str = None
    ) -> str:
        """
        翻译 PDF 文件，保留原始布局
        
        Args:
            input_path: 输入 PDF 路径
            output_path: 输出 PDF 路径（默认在 output 目录）
            font_path: 自定义字体路径（用于英文显示）
        
        Returns:
            输出文件路径
        """
        input_path = Path(input_path)
        if output_path is None:
            output_path = OUTPUT_DIR / f"{input_path.stem}_EN.pdf"
        
        print(f"📄 开始翻译: {input_path.name}")
        
        # Step 1: 提取中文文本
        print("\n🔍 Step 1: 提取中文文本...")
        text_blocks = self.extract_text_blocks(str(input_path))
        chinese_texts = [b["text"] for b in text_blocks]
        print(f"   找到 {len(chinese_texts)} 个中文文本块")
        
        if not chinese_texts:
            print("   没有找到中文内容，直接复制文件")
            import shutil
            shutil.copy(input_path, output_path)
            return str(output_path)
        
        # Step 2: 批量翻译
        print("\n🤖 Step 2: AI 翻译...")
        translations = self.batch_translate(chinese_texts)
        print(f"   翻译完成: {len(translations)} 条")
        
        # Step 3: 替换文本
        print("\n✏️  Step 3: 替换文本...")
        doc = fitz.open(str(input_path))
        
        # 获取字体用于精确测量
        font = fitz.Font("helv")
        
        # === 第一阶段：按字体大小分组，计算每组的缩放比例 ===
        # 将字体大小四舍五入到整数作为分组依据
        size_groups = {}  # {rounded_size: [items]}
        
        for block in text_blocks:
            original = block["text"]
            translated = translations.get(original)
            
            if translated and translated != original:
                bbox = block.get("bbox")
                if bbox:
                    rect = fitz.Rect(bbox)
                    max_width = rect.width
                    original_size = block.get("size", 10)
                    rounded_size = round(original_size)
                    
                    # 用原始字体大小测量英文宽度
                    text_width = font.text_length(translated, fontsize=original_size)
                    
                    # 计算需要的缩放比例
                    if text_width > max_width:
                        ratio = max_width / text_width
                    else:
                        ratio = 1.0
                    
                    item = {
                        "block": block,
                        "translated": translated,
                        "ratio": ratio,
                        "original_size": original_size
                    }
                    
                    if rounded_size not in size_groups:
                        size_groups[rounded_size] = []
                    size_groups[rounded_size].append(item)
        
        # === 第二阶段：计算每个字体大小组的统一缩放比例 ===
        group_ratios = {}
        for size, items in size_groups.items():
            ratios = [item["ratio"] for item in items]
            # 使用该组最小缩放比例，但不低于 0.6
            group_ratios[size] = max(min(ratios), 0.6)
        
        print(f"   字体分组: {len(size_groups)} 组")
        for size in sorted(size_groups.keys()):
            print(f"      {size}pt: {len(size_groups[size])} 个文本块, 缩放比例 {group_ratios[size]:.2f}")
        
        # === 第三阶段：应用分组缩放比例替换文本 ===
        replaced_count = 0
        for rounded_size, items in size_groups.items():
            group_ratio = group_ratios[rounded_size]
            
            for item in items:
                block = item["block"]
                translated = item["translated"]
                
                page = doc[block["page"]]
                bbox = block.get("bbox")
                rect = fitz.Rect(bbox)
                
                # 用白色矩形覆盖原文
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                
                # 使用该组统一缩放后的字体大小
                original_size = item["original_size"]
                font_size = original_size * group_ratio
                
                # 确保字体不会太小（最小 5pt）
                font_size = max(font_size, 5)
                
                try:
                    origin = block.get("origin")
                    if origin:
                        page.insert_text(
                            origin,
                            translated,
                            fontsize=font_size,
                            fontname="helv",
                            color=(0, 0, 0)
                        )
                    else:
                        page.insert_text(
                            (rect.x0, rect.y1 - font_size * 0.2),
                            translated,
                            fontsize=font_size,
                            fontname="helv",
                            color=(0, 0, 0)
                        )
                    
                    replaced_count += 1
                except Exception as e:
                    print(f"   警告: 替换失败 '{block['text'][:20]}...': {e}")
        
        print(f"   替换了 {replaced_count} 处文本")
        
        # Step 4: 保存
        print("\n💾 Step 4: 保存文件...")
        doc.save(str(output_path))
        doc.close()
        
        print(f"\n✅ 完成! 输出文件: {output_path}")
        return str(output_path)


def translate_pdf_inplace(
    pdf_path: str,
    api_key: str = None,
    model: str = None,
    output_path: str = None
) -> str:
    """
    便捷函数：原位翻译 PDF
    """
    translator = PDFInplaceTranslator(api_key=api_key, model=model)
    return translator.translate_pdf(pdf_path, output_path)
