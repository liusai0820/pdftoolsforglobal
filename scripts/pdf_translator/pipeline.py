"""
主处理流水线
PDF → 分析 → 翻译 → 生成 Datasheet/Manual
"""
import json
from pathlib import Path
from datetime import datetime
from .config import OUTPUT_DIR, TEMP_DIR, LOGO_PATH
from .pdf_extractor import pdf_to_images, extract_embedded_images
from .ai_processor import AIProcessor
from .pdf_renderer import (
    render_datasheet_pdf, 
    render_manual_pdf, 
    save_markdown
)


class TranslationPipeline:
    def __init__(self, api_key: str = None, model: str = None):
        self.ai = AIProcessor(api_key=api_key, model=model)
        self.results = {}
    
    def _insert_images(self, md_content: str, embedded_images: list, images_dir: Path, doc_info: dict = None) -> str:
        """将图片占位符替换为实际图片引用，并添加图例表"""
        if not embedded_images:
            return md_content
        
        # 从 doc_info 获取图片描述信息
        image_descriptions = {}
        if doc_info and "images" in doc_info:
            for img_info in doc_info["images"]:
                img_type = img_info.get("type", "other")
                if img_type not in image_descriptions:
                    image_descriptions[img_type] = img_info.get("description", "")
        
        # 按类型分类图片
        product_img = None
        wiring_img = None
        dimension_img = None
        
        for img in embedded_images:
            img_name = Path(img["image_path"]).name
            w, h = img.get("width", 0), img.get("height", 0)
            
            if w > 200 and h > 200:
                if product_img is None:
                    product_img = img_name
                elif wiring_img is None:
                    wiring_img = img_name
                elif dimension_img is None:
                    dimension_img = img_name
        
        # 替换占位符并添加图例
        if product_img:
            product_legend = self._generate_image_legend("product", doc_info)
            md_content = md_content.replace(
                "<!-- PRODUCT_IMAGE -->", 
                f"![Product Image]({images_dir}/{product_img})\n\n{product_legend}"
            )
        if wiring_img:
            wiring_legend = self._generate_image_legend("wiring", doc_info)
            md_content = md_content.replace(
                "<!-- WIRING_IMAGE -->", 
                f"![Wiring Diagram]({images_dir}/{wiring_img})\n\n{wiring_legend}"
            )
        if dimension_img:
            md_content = md_content.replace(
                "<!-- DIMENSION_IMAGE -->", 
                f"![Dimensions]({images_dir}/{dimension_img})"
            )
        
        # 清理未替换的占位符
        md_content = md_content.replace("<!-- PRODUCT_IMAGE -->", "")
        md_content = md_content.replace("<!-- WIRING_IMAGE -->", "")
        md_content = md_content.replace("<!-- DIMENSION_IMAGE -->", "")
        
        return md_content
    
    def _generate_image_legend(self, img_type: str, doc_info: dict) -> str:
        """生成图片图例表"""
        if not doc_info:
            return ""
        
        if img_type == "wiring" and "wiring" in doc_info:
            wiring = doc_info["wiring"]
            pins = wiring.get("pins", [])
            if pins:
                legend = "*Figure: Wiring Diagram Legend*\n\n"
                legend += "| Wire Color | Function |\n|------------|----------|\n"
                # 中文颜色映射
                color_map = {
                    "棕": "Brown", "蓝": "Blue", "黑": "Black", 
                    "白": "White", "黄": "Yellow", "绿": "Green",
                    "红": "Red", "橙": "Orange"
                }
                for pin in pins:
                    color_cn = pin.get("color", "")
                    color_en = color_map.get(color_cn, color_cn)
                    func = pin.get("function", "")
                    legend += f"| {color_en} | {func} |\n"
                return legend
        
        return ""
    
    def process(
        self, 
        pdf_path: str, 
        output_formats: list = None,
        save_intermediate: bool = True
    ) -> dict:
        """
        处理 PDF 文档
        
        Args:
            pdf_path: 输入 PDF 路径
            output_formats: 输出格式列表 ["datasheet", "manual", "markdown"]
            save_intermediate: 是否保存中间文件
        
        Returns:
            处理结果字典
        """
        if output_formats is None:
            output_formats = ["datasheet", "manual", "markdown"]
        
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")
        
        pdf_name = pdf_path.stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_subdir = OUTPUT_DIR / f"{pdf_name}_{timestamp}"
        output_subdir.mkdir(parents=True, exist_ok=True)
        
        print(f"📄 开始处理: {pdf_path.name}")
        print(f"📁 输出目录: {output_subdir}")
        
        # Step 1: 提取 PDF 页面为图片
        print("\n🔍 Step 1: 提取 PDF 页面...")
        page_images = pdf_to_images(str(pdf_path))
        print(f"   提取了 {len(page_images)} 页")
        
        # Step 2: 提取嵌入图片
        print("\n🖼️  Step 2: 提取嵌入图片...")
        embedded_images = extract_embedded_images(str(pdf_path))
        print(f"   提取了 {len(embedded_images)} 张图片")
        
        # 复制图片到输出目录
        images_dir = output_subdir / "images"
        images_dir.mkdir(exist_ok=True)
        for img in embedded_images:
            src = Path(img["image_path"])
            dst = images_dir / src.name
            if src.exists():
                import shutil
                shutil.copy(src, dst)
        
        # Step 3: AI 分析文档内容
        print("\n🤖 Step 3: AI 分析文档内容...")
        doc_info = self.ai.analyze_pdf_pages(page_images)
        
        if save_intermediate:
            info_path = output_subdir / "doc_info.json"
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(doc_info, f, ensure_ascii=False, indent=2)
            print(f"   保存分析结果: {info_path}")
        
        # 获取产品名称 - 优先使用英文型号
        model_name = doc_info.get("model", "")
        # 如果有型号，直接用型号作为标题（纯英文）
        if model_name:
            full_name = model_name
        else:
            full_name = pdf_name
        
        results = {
            "pdf_name": pdf_name,
            "product_name": full_name,
            "output_dir": str(output_subdir),
            "files": {}
        }
        
        # Step 4: 生成 Datasheet
        if "datasheet" in output_formats:
            print("\n📋 Step 4: 生成 Datasheet...")
            datasheet_md = self.ai.generate_datasheet(doc_info, embedded_images)
            
            # 替换图片占位符为实际图片
            datasheet_md = self._insert_images(datasheet_md, embedded_images, images_dir, doc_info)
            
            # 保存 Markdown
            if "markdown" in output_formats:
                md_path = output_subdir / f"{pdf_name}_datasheet.md"
                save_markdown(datasheet_md, str(md_path))
                results["files"]["datasheet_md"] = str(md_path)
                print(f"   保存 Markdown: {md_path}")
            
            # 渲染 PDF
            pdf_output = output_subdir / f"{pdf_name}_Datasheet_EN.pdf"
            render_datasheet_pdf(
                datasheet_md,
                str(pdf_output),
                product_name=full_name,
                logo_path=str(LOGO_PATH) if LOGO_PATH.exists() else None,
                images_dir=str(images_dir)
            )
            results["files"]["datasheet_pdf"] = str(pdf_output)
            print(f"   生成 PDF: {pdf_output}")
        
        # Step 5: 生成 User Manual
        if "manual" in output_formats:
            print("\n📖 Step 5: 生成 User Manual...")
            manual_md = self.ai.generate_user_manual(doc_info, embedded_images)
            
            # 替换图片占位符为实际图片
            manual_md = self._insert_images(manual_md, embedded_images, images_dir, doc_info)
            
            # 保存 Markdown
            if "markdown" in output_formats:
                md_path = output_subdir / f"{pdf_name}_manual.md"
                save_markdown(manual_md, str(md_path))
                results["files"]["manual_md"] = str(md_path)
                print(f"   保存 Markdown: {md_path}")
            
            # 渲染 PDF
            pdf_output = output_subdir / f"{pdf_name}_UserManual_EN.pdf"
            render_manual_pdf(
                manual_md,
                str(pdf_output),
                product_name=full_name,
                logo_path=str(LOGO_PATH) if LOGO_PATH.exists() else None,
                images_dir=str(images_dir)
            )
            results["files"]["manual_pdf"] = str(pdf_output)
            print(f"   生成 PDF: {pdf_output}")
        
        print("\n✅ 处理完成!")
        print(f"   输出目录: {output_subdir}")
        
        self.results = results
        return results


def translate_pdf(
    pdf_path: str,
    api_key: str = None,
    model: str = None,
    output_formats: list = None
) -> dict:
    """
    便捷函数：翻译 PDF 文档
    
    Args:
        pdf_path: PDF 文件路径
        api_key: OpenRouter API Key
        model: 模型名称 (默认 gemini-2.5-flash)
        output_formats: 输出格式 ["datasheet", "manual", "markdown"]
    
    Returns:
        处理结果
    """
    pipeline = TranslationPipeline(api_key=api_key, model=model)
    return pipeline.process(pdf_path, output_formats=output_formats)
