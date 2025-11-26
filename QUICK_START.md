# 快速开始

## 5 分钟本地运行

### 1️⃣ 安装依赖
```bash
pip install -r requirements.txt
```

### 2️⃣ 配置 API Key
```bash
cp .env.example .env
# 编辑 .env，设置 OPENROUTER_API_KEY
```

### 3️⃣ 测试环境
```bash
python test.py
```

### 4️⃣ 启动应用
```bash
python app/main.py
```

### 5️⃣ 打开浏览器
```
http://localhost:5000
```

---

## 部署到 Render（10 分钟）

### 1️⃣ 推送到 GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2️⃣ 在 Render 创建服务
- 访问 https://dashboard.render.com
- 点击 "New +" → "Web Service"
- 选择你的 GitHub 仓库
- 配置：
  - Build: `pip install -r requirements.txt`
  - Start: `gunicorn app.main:app`

### 3️⃣ 设置环境变量
- 在 Render 中添加 Secret：
  - Key: `OPENROUTER_API_KEY`
  - Value: 你的 API Key

### 4️⃣ 部署
- 点击 "Deploy"
- 等待 2-5 分钟
- 获得公开 URL

---

## 功能使用

### PDF 翻译
1. 选择 "🌐 PDF翻译"
2. 上传 PDF
3. 点击 "开始处理"
4. 下载翻译后的 PDF

### 颜色替换
1. 选择 "🎨 颜色替换"
2. 上传 PDF
3. 设置源颜色和目标颜色
4. 点击 "开始处理"
5. 下载处理后的 PDF

---

## 常用命令

```bash
# 测试环境
python test.py

# 启动应用
python app/main.py

# 使用启动脚本
bash run.sh
```

---

## 故障排除

**应用无法启动？**
- 检查 `.env` 文件是否存在
- 验证 `OPENROUTER_API_KEY` 是否设置
- 运行 `python test.py` 检查依赖

**部署失败？**
- 查看 Render 的构建日志
- 检查 `requirements.txt` 中的依赖
- 确保所有文件都已提交到 GitHub

---

**准备好了？开始吧！** 🚀
