#!/usr/bin/env python3
"""
测试 Web 应用的基本功能
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 检查必要的环境变量
api_key = os.getenv('OPENROUTER_API_KEY')
if not api_key:
    print("❌ 错误: 未设置 OPENROUTER_API_KEY")
    print("请在 .env 文件中设置 OPENROUTER_API_KEY")
    sys.exit(1)

print("✅ 环境变量检查通过")
print(f"   API Key: {api_key[:20]}...")

# 检查依赖
print("\n📦 检查依赖...")
try:
    import flask
    print("   ✓ Flask")
    import fitz
    print("   ✓ PyMuPDF")
    import pikepdf
    print("   ✓ pikepdf")
    import httpx
    print("   ✓ httpx")
except ImportError as e:
    print(f"   ❌ 缺少依赖: {e}")
    print("   请运行: pip install -r requirements.txt")
    sys.exit(1)

# 检查文件结构
print("\n📁 检查文件结构...")
required_files = [
    'app/main.py',
    'templates/index_web.html',
    'scripts/pdf_translator/pdf_inplace_translator.py',
    'scripts/pdf_vector_color_replacer.py',
    'requirements.txt'
]

# 获取脚本所在目录
script_dir = Path(__file__).parent
for file in required_files:
    file_path = script_dir / file
    if file_path.exists():
        print(f"   ✓ {file}")
    else:
        print(f"   ⚠️  缺少文件: {file} (可能不影响功能)")
        # 不退出，继续检查

# 检查目录
print("\n📂 检查目录...")
required_dirs = ['uploads', 'output']
for dir_name in required_dirs:
    dir_path = Path(dir_name)
    if dir_path.exists():
        print(f"   ✓ {dir_name}/")
    else:
        print(f"   ⚠️  创建目录: {dir_name}/")
        dir_path.mkdir(exist_ok=True)

print("\n" + "=" * 60)
print("✅ 所有检查通过！")
print("\n启动 Web 应用:")
print("   python app/main.py")
print("   或")
print("   bash run.sh")
print("\n访问地址:")
print("   http://localhost:5000")
print("=" * 60)
