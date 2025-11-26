# 项目结构说明

## 📁 完整目录结构

```
pdf-processor-web/
│
├── app/                              # 应用代码
│   └── main.py                       # Flask 应用主文件
│
├── templates/                        # HTML 模板
│   └── index_web.html               # Web UI
│
├── scripts/                          # PDF 处理脚本
│   ├── pdf_translator/              # PDF 翻译模块
│   │   ├── __init__.py
│   │   ├── pdf_inplace_translator.py
│   │   ├── ai_processor.py
│   │   ├── config.py
│   │   ├── pipeline.py
│   │   └── ...
│   └── pdf_vector_color_replacer.py # 颜色替换脚本
│
├── uploads/                          # 用户上传的文件
│   └── .gitkeep
│
├── output/                           # 处理后的输出文件
│   └── .gitkeep
│
├── docs/                             # 文档（可选）
│
├── requirements.txt                  # Python 依赖
├── .env.example                     # 环境变量示例
├── .gitignore                       # Git 忽略配置
├── render.yaml                      # Render 部署配置
├── run.sh                           # 启动脚本
├── test.py                          # 测试脚本
├── README.md                        # 项目说明
├── QUICK_START.md                   # 快速开始指南
├── DEPLOYMENT.md                    # 部署指南
└── PROJECT_STRUCTURE.md             # 本文件
```

## 📝 文件说明

### 核心应用文件

#### `app/main.py`
- **作用**：Flask Web 应用主文件
- **功能**：
  - 处理 HTTP 请求
  - 管理文件上传和下载
  - 调用 PDF 处理模块
  - 提供 REST API 端点
- **修改**：添加新功能时编辑此文件

#### `templates/index_web.html`
- **作用**：Web 用户界面
- **功能**：
  - 提供两个功能模块的交互界面
  - 处理文件上传
  - 显示处理结果
  - 响应式设计
- **修改**：自定义 UI 时编辑此文件

### 脚本文件

#### `scripts/pdf_translator/`
- **作用**：PDF 翻译模块
- **主要文件**：
  - `pdf_inplace_translator.py` - 核心翻译逻辑
  - `ai_processor.py` - AI 处理接口
  - `config.py` - 配置文件

#### `scripts/pdf_vector_color_replacer.py`
- **作用**：颜色替换脚本
- **功能**：
  - 识别 PDF 中的颜色
  - 替换为目标颜色
  - 保留矢量状态

### 配置文件

#### `requirements.txt`
- **作用**：Python 依赖列表
- **内容**：
  - Flask - Web 框架
  - PyMuPDF - PDF 处理
  - pikepdf - PDF 矢量操作
  - httpx - HTTP 客户端
  - gunicorn - WSGI 服务器

#### `.env.example`
- **作用**：环境变量示例
- **用途**：复制为 `.env` 并填入实际值

#### `render.yaml`
- **作用**：Render 部署配置
- **内容**：
  - 服务名称
  - 构建命令
  - 启动命令
  - 环境变量

#### `.gitignore`
- **作用**：Git 忽略配置
- **忽略内容**：
  - `.env` - 敏感信息
  - `__pycache__/` - Python 缓存
  - `*.pyc` - 编译文件
  - `.DS_Store` - macOS 文件

### 文档文件

#### `README.md`
- **作用**：项目说明文档
- **内容**：
  - 功能介绍
  - 快速开始
  - 使用说明
  - API 文档

#### `QUICK_START.md`
- **作用**：快速开始指南
- **内容**：
  - 5 分钟本地运行
  - 10 分钟部署到 Render
  - 常用命令

#### `DEPLOYMENT.md`
- **作用**：详细部署指南
- **内容**：
  - 部署检查清单
  - 常见问题
  - 故障排除

### 脚本文件

#### `run.sh`
- **作用**：启动脚本
- **功能**：
  - 检查环境
  - 安装依赖
  - 启动应用

#### `test.py`
- **作用**：测试脚本
- **功能**：
  - 检查环境变量
  - 检查依赖
  - 检查文件结构

### 目录说明

#### `uploads/`
- **作用**：存储用户上传的 PDF 文件
- **特点**：
  - 临时存储
  - 自动清理
  - 不提交到 Git

#### `output/`
- **作用**：存储处理后的 PDF 文件
- **特点**：
  - 临时存储
  - 用户下载后删除
  - 不提交到 Git

#### `docs/`
- **作用**：额外文档（可选）
- **用途**：存储详细的技术文档

## 🔄 工作流程

### 本地开发流程

```
1. 用户上传 PDF
   ↓
2. Flask 接收文件
   ↓
3. 保存到 uploads/ 目录
   ↓
4. 调用 PDF 处理脚本
   ↓
5. 处理后保存到 output/ 目录
   ↓
6. 返回下载链接
   ↓
7. 用户下载文件
```

### 部署流程

```
1. 本地开发完成
   ↓
2. 推送到 GitHub
   ↓
3. Render 自动构建
   ↓
4. 安装依赖
   ↓
5. 启动应用
   ↓
6. 获得公开 URL
```

## 📊 文件大小参考

| 文件 | 大小 | 说明 |
|------|------|------|
| `app/main.py` | ~8KB | 核心应用 |
| `templates/index_web.html` | ~15KB | 前端 UI |
| `requirements.txt` | <1KB | 依赖列表 |
| `scripts/` | ~50KB | 处理脚本 |
| **总计** | ~75KB | 源代码 |

## 🔐 安全考虑

### 敏感文件

⚠️ **不要提交到 GitHub：**
- `.env` - 包含 API Key
- `uploads/` - 用户上传的文件
- `output/` - 处理后的文件
- `__pycache__/` - Python 缓存

✅ **已配置在 .gitignore 中**

### 文件权限

- `run.sh` - 需要执行权限
- `test.py` - 需要执行权限

## 🚀 部署包内容

部署到 Render 时，以下文件会被上传：

```
✅ app/main.py
✅ templates/index_web.html
✅ requirements.txt
✅ render.yaml
✅ scripts/pdf_translator/
✅ scripts/pdf_vector_color_replacer.py
❌ .env (不上传，在 Render 中设置)
❌ uploads/ (不上传)
❌ output/ (不上传)
```

## 📖 推荐阅读顺序

1. **第一次使用**
   - `README.md` - 项目说明
   - `QUICK_START.md` - 快速开始

2. **准备部署**
   - `DEPLOYMENT.md` - 部署指南

3. **深入了解**
   - `PROJECT_STRUCTURE.md` - 本文件
   - 源代码注释

## 🔧 常见修改

### 修改文件大小限制

编辑 `app/main.py`：
```python
MAX_FILE_SIZE = 100 * 1024 * 1024  # 改为 100MB
```

### 修改上传/输出目录

编辑 `app/main.py`：
```python
UPLOAD_FOLDER = PROJECT_ROOT / 'my_uploads'
OUTPUT_FOLDER = PROJECT_ROOT / 'my_output'
```

### 添加新的 API 端点

在 `app/main.py` 中添加：
```python
@app.route('/api/new-endpoint', methods=['POST'])
def new_endpoint():
    # 你的代码
    pass
```

## 📞 获取帮助

- 查看 `README.md` 了解功能
- 查看 `QUICK_START.md` 快速上手
- 查看 `DEPLOYMENT.md` 部署问题
- 查看源代码注释

---

**版本**：1.0.0
**最后更新**：2024 年
**状态**：生产就绪
