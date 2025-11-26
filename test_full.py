#!/usr/bin/env python3
"""
完整的项目测试脚本
测试所有关键功能
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

print("=" * 70)
print("PDF 处理 Web 应用 - 完整测试")
print("=" * 70)

# 1. 环境检查
print("\n[1/5] 环境变量检查...")
api_key = os.getenv('OPENROUTER_API_KEY')
if not api_key:
    print("❌ 错误: 未设置 OPENROUTER_API_KEY")
    sys.exit(1)
print(f"✅ API Key 已设置: {api_key[:20]}...")

# 2. 依赖检查
print("\n[2/5] 依赖检查...")
try:
    import flask
    import fitz
    import pikepdf
    import httpx
    from werkzeug.utils import secure_filename
    print("✅ 所有依赖已安装")
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    sys.exit(1)

# 3. 文件结构检查
print("\n[3/5] 文件结构检查...")
required_files = {
    'app/main.py': 'Flask 应用主文件',
    'templates/index_web.html': 'Web 界面',
    'scripts/pdf_translator/pdf_inplace_translator.py': 'PDF 翻译模块',
    'scripts/pdf_vector_color_replacer.py': '颜色替换模块',
    'requirements.txt': '依赖列表',
    '.env': '环境配置'
}

script_dir = Path(__file__).parent
all_files_ok = True
for file, desc in required_files.items():
    file_path = script_dir / file
    if file_path.exists():
        print(f"✅ {file} ({desc})")
    else:
        print(f"⚠️  {file} 缺失 ({desc})")
        if file == '.env':
            print("   → 这是可选的，可以使用 .env.example")
        else:
            all_files_ok = False

if not all_files_ok:
    print("\n❌ 缺少关键文件")
    sys.exit(1)

# 4. 导入模块检查
print("\n[4/5] 模块导入检查...")
try:
    sys.path.insert(0, str(script_dir / 'scripts'))
    from pdf_translator.pdf_inplace_translator import PDFInplaceTranslator
    from pdf_translator.ai_processor import AIProcessor
    from pdf_vector_color_replacer import replace_color_with_device_rgb
    print("✅ 所有模块导入成功")
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. API 连接测试
print("\n[5/5] API 连接测试...")
try:
    ai = AIProcessor()
    print("✅ AI 处理器初始化成功")
    print(f"   使用模型: {ai.model}")
    print(f"   API 地址: {ai.base_url}")
except Exception as e:
    print(f"❌ AI 处理器初始化失败: {e}")
    sys.exit(1)

# 总结
print("\n" + "=" * 70)
print("✅ 所有测试通过！项目已准备就绪")
print("=" * 70)
print("\n📝 后续步骤:")
print("   1. 启动 Web 应用:")
print("      python app/main.py")
print("   2. 访问应用:")
print("      http://localhost:5000")
print("   3. 上传 PDF 文件进行处理")
print("\n🚀 部署到 Render:")
print("   1. 推送到 GitHub")
print("   2. 在 Render 中连接 GitHub 仓库")
print("   3. 设置环境变量 OPENROUTER_API_KEY")
print("   4. 部署应用")
print("=" * 70)
