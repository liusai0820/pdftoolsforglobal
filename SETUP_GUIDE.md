# 完整设置指南

## 🎯 项目概述

这是一个独立的 PDF 处理 Web 应用项目，包含：
- ✅ PDF 翻译功能
- ✅ 颜色替换功能
- ✅ 完整的 Web UI
- ✅ Render 部署配置

## 📦 项目包含的文件

```
pdf-processor-web/
├── app/main.py                    # Flask 应用
├── templates/index_web.html       # Web UI
├── scripts/                       # PDF 处理脚本
├── uploads/                       # 上传文件夹
├── output/                        # 输出文件夹
├── requirements.txt               # 依赖
├── .env.example                  # 环境变量示例
├── render.yaml                   # Render 配置
├── run.sh                        # 启动脚本
├── test.py                       # 测试脚本
├── README.md                     # 项目说明
├── QUICK_START.md                # 快速开始
├── DEPLOYMENT.md                 # 部署指南
└── PROJECT_STRUCTURE.md          # 项目结构
```

## 🚀 快速开始（5 分钟）

### 1. 安装依赖
```bash
cd pdf-processor-web
pip install -r requirements.txt
```

### 2. 配置环境
```bash
cp .env.example .env
# 编辑 .env，设置 OPENROUTER_API_KEY
```

### 3. 测试环境
```bash
python test.py
```

### 4. 启动应用
```bash
python app/main.py
```

### 5. 访问应用
```
http://localhost:5000
```

## 📋 部署到 Render（10 分钟）

### 1. 推送到 GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. 在 Render 创建服务
- 访问 https://dashboard.render.com
- 点击 "New +" → "Web Service"
- 选择你的 GitHub 仓库
- 配置：
  - Build: `pip install -r requirements.txt`
  - Start: `gunicorn app.main:app`

### 3. 设置环境变量
- 添加 Secret：
  - Key: `OPENROUTER_API_KEY`
  - Value: 你的 API Key

### 4. 部署
- 点击 "Deploy"
- 等待完成
- 获得公开 URL

## 📖 文档导航

| 文档 | 用途 | 阅读时间 |
|------|------|---------|
| `README.md` | 项目说明 | 10 分钟 |
| `QUICK_START.md` | 快速上手 | 5 分钟 |
| `DEPLOYMENT.md` | 部署指南 | 15 分钟 |
| `PROJECT_STRUCTURE.md` | 项目结构 | 10 分钟 |

## 🎯 功能使用

### PDF 翻译
1. 选择 "🌐 PDF翻译"
2. 上传 PDF
3. 点击 "开始处理"
4. 下载翻译后的 PDF

### 颜色替换
1. 选择 "🎨 颜色替换"
2. 上传 PDF
3. 设置颜色
4. 点击 "开始处理"
5. 下载处理后的 PDF

## 🔧 常用命令

```bash
# 测试环境
python test.py

# 启动应用
python app/main.py

# 使用启动脚本
bash run.sh

# 安装依赖
pip install -r requirements.txt
```

## ✅ 检查清单

### 本地开发
- [ ] 安装了依赖
- [ ] 配置了 .env
- [ ] 运行了 test.py
- [ ] 启动了应用
- [ ] 访问了 http://localhost:5000

### 部署前
- [ ] 推送到 GitHub
- [ ] 在 Render 创建了服务
- [ ] 设置了环境变量
- [ ] 点击了 Deploy

### 部署后
- [ ] 访问了部署 URL
- [ ] 测试了翻译功能
- [ ] 测试了颜色替换功能
- [ ] 下载了处理后的文件

## 🐛 故障排除

### 应用无法启动
```bash
# 检查环境
python test.py

# 检查 .env 文件
cat .env

# 检查依赖
pip list | grep Flask
```

### 部署失败
- 查看 Render 的构建日志
- 检查 requirements.txt
- 确保文件已提交到 GitHub

### 功能不工作
- 检查浏览器控制台
- 查看 Render 的应用日志
- 验证 API Key

## 📞 获取帮助

1. 查看 `README.md` 了解功能
2. 查看 `QUICK_START.md` 快速上手
3. 查看 `DEPLOYMENT.md` 部署问题
4. 查看 `PROJECT_STRUCTURE.md` 项目结构

## 🎉 完成！

现在你有一个完整的 PDF 处理 Web 应用，可以：
- ✅ 在本地运行
- ✅ 部署到 Render
- ✅ 与他人分享
- ✅ 继续开发

祝你使用愉快！🚀

---

**版本**：1.0.0
**状态**：生产就绪
