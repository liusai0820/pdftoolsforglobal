#!/usr/bin/env python3
"""
命令行工具
用法: python -m scripts.pdf_translator.cli input.pdf [options]
"""
import argparse
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.pdf_translator.pipeline import translate_pdf
from scripts.pdf_translator.config import DEFAULT_MODEL


def main():
    parser = argparse.ArgumentParser(
        description="中文技术文档翻译工具 - 生成英文 Datasheet 和 User Manual",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  python -m scripts.pdf_translator.cli materials/沃米（LA-W500）.pdf
  
  # 指定 API Key
  python -m scripts.pdf_translator.cli input.pdf --api-key YOUR_KEY
  
  # 只生成 Datasheet
  python -m scripts.pdf_translator.cli input.pdf --format datasheet
  
  # 使用其他模型
  python -m scripts.pdf_translator.cli input.pdf --model google/gemini-2.0-flash-exp
        """
    )
    
    parser.add_argument(
        "pdf_path",
        help="输入 PDF 文件路径"
    )
    
    parser.add_argument(
        "--api-key", "-k",
        help="OpenRouter API Key (也可通过 OPENROUTER_API_KEY 环境变量设置)",
        default=os.getenv("OPENROUTER_API_KEY")
    )
    
    parser.add_argument(
        "--model", "-m",
        help=f"AI 模型 (默认: {DEFAULT_MODEL})",
        default=DEFAULT_MODEL
    )
    
    parser.add_argument(
        "--format", "-f",
        nargs="+",
        choices=["datasheet", "manual", "markdown"],
        default=["datasheet", "manual", "markdown"],
        help="输出格式 (默认: 全部)"
    )
    
    parser.add_argument(
        "--no-intermediate",
        action="store_true",
        help="不保存中间文件 (doc_info.json)"
    )
    
    args = parser.parse_args()
    
    # 检查 API Key
    if not args.api_key:
        print("❌ 错误: 请设置 OPENROUTER_API_KEY 环境变量或使用 --api-key 参数")
        print("   获取 API Key: https://openrouter.ai/keys")
        sys.exit(1)
    
    # 检查文件存在
    if not Path(args.pdf_path).exists():
        print(f"❌ 错误: 文件不存在: {args.pdf_path}")
        sys.exit(1)
    
    try:
        results = translate_pdf(
            pdf_path=args.pdf_path,
            api_key=args.api_key,
            model=args.model,
            output_formats=args.format
        )
        
        print("\n" + "=" * 50)
        print("📦 生成的文件:")
        for name, path in results.get("files", {}).items():
            print(f"   • {name}: {path}")
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
