# PDF 技术文档翻译工具

将中文技术文档（PDF）自动翻译并生成专业的英文 Datasheet 和 User Manual。

## 工作流程

```
中文 PDF → AI 视觉识别 → 结构化提取 → 翻译重组 → Markdown → PDF 渲染
```

## 特点

- **智能识别**: 使用 Gemini Vision 直接识别 PDF 页面，保留完整信息
- **结构化输出**: 自动提取技术规格、接线说明、安全警告等
- **双版本输出**: 
  - Datasheet: 1-2页，突出技术规格，适合销售
  - User Manual: 完整手册，包含安装、操作、安全说明
- **专业排版**: 使用 CSS 控制样式，符合国际技术文档规范
- **图片处理**: 自动提取嵌入图片，生成英文图例

## 安装

```bash
pip install -r requirements.txt
```

macOS 需要额外安装 WeasyPrint 依赖:
```bash
brew install pango
```

## 使用方法

### 1. 命令行模式

```bash
# 设置 API Key
export OPENROUTER_API_KEY="sk-or-..."

# 翻译 PDF
python translate_pdf.py materials/沃米（LA-W500）.pdf

# 指定输出格式
python translate_pdf.py input.pdf --format datasheet manual

# 使用其他模型
python translate_pdf.py input.pdf --model anthropic/claude-3.5-sonnet
```

### 2. Web 界面模式

```bash
python translate_pdf.py --web
# 访问 http://localhost:8889
```

### 3. Python API

```python
from scripts.pdf_translator import translate_pdf

results = translate_pdf(
    pdf_path="materials/沃米（LA-W500）.pdf",
    api_key="sk-or-...",
    model="google/gemini-2.5-flash",
    output_formats=["datasheet", "manual", "markdown"]
)

print(results["files"])
```

## 输出文件

```
output/
└── 沃米（LA-W500）_20241125_143022/
    ├── doc_info.json           # AI 提取的结构化信息
    ├── 沃米（LA-W500）_datasheet.md    # Datasheet Markdown
    ├── 沃米（LA-W500）_Datasheet_EN.pdf # Datasheet PDF
    ├── 沃米（LA-W500）_manual.md       # Manual Markdown
    ├── 沃米（LA-W500）_UserManual_EN.pdf # Manual PDF
    └── images/                  # 提取的图片
```

## 配置

编辑 `scripts/pdf_translator/config.py`:

```python
# 公司信息（显示在页脚）
COMPANY_NAME = "VOLSENTEC"
COMPANY_WEBSITE = "www.volsentec.com"

# Logo 路径
LOGO_PATH = BASE_DIR / "materials" / "logo.png"

# 默认模型
DEFAULT_MODEL = "google/gemini-2.5-flash"
```

## 支持的模型

通过 OpenRouter 支持多种模型:

| 模型 | 特点 |
|------|------|
| google/gemini-2.5-flash | 推荐，速度快，多模态能力强 |
| google/gemini-2.0-flash-exp | 最新版本 |
| anthropic/claude-3.5-sonnet | 翻译质量高 |
| openai/gpt-4o | 综合能力强 |

## 获取 API Key

1. 访问 https://openrouter.ai/keys
2. 注册并创建 API Key
3. 设置环境变量或在 Web 界面输入

## 常见问题

### Q: 图片中的中文标注怎么处理？

A: 工具会自动提取图片并生成英文图例（Legend），而不是直接修改图片。这是更稳定的方案。

### Q: 表格排版错乱怎么办？

A: 检查生成的 Markdown 文件，手动调整后重新渲染。或者调整 CSS 样式。

### Q: 如何自定义样式？

A: 编辑 `scripts/pdf_translator/pdf_renderer.py` 中的 CSS 样式。
