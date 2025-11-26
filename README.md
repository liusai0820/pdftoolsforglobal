# PDF 处理工具 Web 应用

一个功能完整的 Web 应用，集成了 PDF 翻译和颜色替换功能。

## 🎯 功能

### 1. PDF 翻译 (🌐)
- 自动识别 PDF 中的中文文本
- 使用 AI 进行精准翻译
- 保留原始 PDF 布局和格式
- 输出文件名: `原名_processed.pdf`

### 2. 颜色替换 (🎨)
- 将 PDF 中的指定 CMYK 颜色替换为目标颜色
- 保留矢量状态，不转换为图片
- 支持自定义颜色选择

## 📁 项目结构

```
pdf-processor-web/
├── app/
│   └── main.py                 # Flask 应用主文件
├── templates/
│   └── index_web.html          # Web UI
├── scripts/
│   ├── pdf_translator/         # PDF 翻译模块
│   └── pdf_vector_color_replacer.py  # 颜色替换脚本
├── uploads/                    # 上传文件夹
├── output/                     # 输出文件夹
├── requirements.txt            # Python 依赖
├── .env.example               # 环境变量示例
├── render.yaml                # Render 部署配置
├── run.sh                     # 启动脚本
├── test.py                    # 测试脚本
└── README.md                  # 本文件
```

## 🚀 快速开始

### 1. 本地开发（5 分钟）

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，设置 OPENROUTER_API_KEY

# 测试环境
python test.py

# 启动应用
python app/main.py
# 或使用启动脚本
bash run.sh

# 访问应用
# http://localhost:5000
```

### 2. 部署到 Render（10 分钟）

#### 准备

1. 推送到 GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. 在 Render 创建 Web Service
   - 访问 https://dashboard.render.com
   - 点击 "New +" → "Web Service"
   - 选择你的 GitHub 仓库
   - 配置：
     - Build: `pip install -r requirements.txt`
     - Start: `gunicorn app.main:app`

3. 设置环境变量
   - 在 Render 中添加 Secret：
     - Key: `OPENROUTER_API_KEY`
     - Value: 你的 API Key

4. 部署
   - 点击 "Deploy"
   - 等待 2-5 分钟
   - 获得公开 URL

## 📖 使用说明

### PDF 翻译

1. 选择 "🌐 PDF翻译" 标签
2. 上传 PDF 文件
3. 点击 "开始处理"
4. 等待翻译完成
5. 点击下载链接获取翻译后的 PDF

### 颜色替换

1. 选择 "🎨 颜色替换" 标签
2. 上传 PDF 文件
3. 设置源颜色 (CMYK 值)
4. 选择目标颜色 (使用颜色选择器或输入十六进制值)
5. 点击 "开始处理"
6. 等待处理完成
7. 点击下载链接获取处理后的 PDF

## 🔧 配置

### 环境变量

| 变量 | 说明 | 必需 | 默认值 |
|------|------|------|--------|
| `OPENROUTER_API_KEY` | OpenRouter API Key | 是 | - |
| `PORT` | 应用端口 | 否 | 5000 |
| `FLASK_ENV` | Flask 环境 | 否 | production |

### 应用配置

在 `app/main.py` 中可以修改：

```python
MAX_FILE_SIZE = 50 * 1024 * 1024  # 最大文件大小（50MB）
```

## 📊 API 端点

### 上传文件
```
POST /api/upload
Content-Type: multipart/form-data

参数：
- file: PDF 文件

响应：
{
  "success": true,
  "filepath": "/path/to/file.pdf",
  "filename": "file.pdf"
}
```

### 处理 PDF
```
POST /api/process
Content-Type: application/json

参数（翻译）：
{
  "input_file": "/path/to/file.pdf",
  "operation": "translate"
}

参数（颜色替换）：
{
  "input_file": "/path/to/file.pdf",
  "operation": "color",
  "source_cmyk": [0.7804, 0.8667, 0, 0],
  "target_hex": "#01beb0"
}

响应：
{
  "success": true,
  "message": "处理完成",
  "download_url": "/api/download/filename_processed.pdf"
}
```

### 下载文件
```
GET /api/download/<filename>

返回：PDF 文件下载
```

### 健康检查
```
GET /health

响应：
{
  "status": "ok"
}
```

## 🛠️ 常用命令

```bash
# 测试环境
python test.py

# 启动应用
python app/main.py

# 使用启动脚本
bash run.sh

# 安装依赖
pip install -r requirements.txt

# 生成依赖列表
pip freeze > requirements.txt
```

## 📋 文件说明

| 文件 | 说明 |
|------|------|
| `app/main.py` | Flask 应用主文件 |
| `templates/index_web.html` | Web UI |
| `scripts/pdf_translator/` | PDF 翻译模块 |
| `scripts/pdf_vector_color_replacer.py` | 颜色替换脚本 |
| `requirements.txt` | Python 依赖 |
| `.env.example` | 环境变量示例 |
| `render.yaml` | Render 部署配置 |
| `run.sh` | 启动脚本 |
| `test.py` | 测试脚本 |

## 🐛 故障排除

### 应用无法启动

1. 检查 `.env` 文件是否存在
2. 验证 `OPENROUTER_API_KEY` 是否设置
3. 运行 `python test.py` 检查依赖

### 部署失败

1. 查看 Render 的构建日志
2. 检查 `requirements.txt` 中的依赖
3. 确保所有文件都已提交到 GitHub

### 功能不工作

1. 检查浏览器控制台的错误
2. 查看 Render 的应用日志
3. 验证 API Key 是否有效

## 📈 性能优化

- 批量翻译优化，减少 API 调用
- 字体缩放，确保翻译文本适应原位置
- 临时文件自动清理
- 支持并发请求

## 🔒 安全特性

- 文件类型验证
- 文件大小限制
- 路径安全检查
- API Key 环境变量存储
- HTTPS 自动启用

## 💰 成本估算

### Render 成本

| 计划 | 月度 | 特点 |
|------|------|------|
| Free | $0 | 750 小时/月 |
| Starter | $7 | 无限运行 |

### OpenRouter 成本

按 API 调用计费，具体价格取决于模型选择。

## 📝 许可证

MIT License

## 🤝 支持

- 📖 查看文档
- 🐛 报告问题
- 💬 获取帮助

---

**版本**：1.0.0
**状态**：生产就绪
