"""
配置文件
"""
import os
from pathlib import Path

# OpenRouter API 配置
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "google/gemini-2.5-flash"

# 目录配置
BASE_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"
ASSETS_DIR = BASE_DIR / "assets"

# 确保目录存在
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

# PDF 转图片配置
PDF_DPI = 200  # 平衡质量和速度

# 文档模板配置
COMPANY_NAME = "VOLSENTEC"
COMPANY_WEBSITE = "www.volsentec.com"
LOGO_PATH = BASE_DIR / "materials" / "logo.png"
