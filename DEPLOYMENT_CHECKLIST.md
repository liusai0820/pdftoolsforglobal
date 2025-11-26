# 部署检查清单

## ✅ 已完成

- [x] 项目代码已推送到 GitHub: https://github.com/liusai0820/pdftoolsforglobal.git
- [x] 所有依赖已在 requirements.txt 中定义
- [x] 环境变量配置已准备 (.env.example)
- [x] Flask 应用已配置完成
- [x] PDF 翻译功能已实现（支持自动换行）
- [x] 颜色替换功能已实现
- [x] Web 界面已完成
- [x] 本地测试已通过

## 🚀 部署到 Render 的步骤

### 1. 在 Render 中创建新服务

1. 访问 https://dashboard.render.com
2. 点击 "New +" → "Web Service"
3. 选择 "Connect a repository"
4. 授权并选择 `pdftoolsforglobal` 仓库

### 2. 配置部署设置

- **Name**: pdf-tools-for-global
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app.main:app`
- **Instance Type**: Starter (或更高)

### 3. 设置环境变量

在 Render 的 "Environment" 部分添加：

```
OPENROUTER_API_KEY=sk-or-v1-...（你的 API Key）
FLASK_ENV=production
```

### 4. 部署

点击 "Create Web Service" 开始部署。部署通常需要 2-5 分钟。

## 📋 部署前检查

- [ ] GitHub 仓库已创建并包含所有代码
- [ ] .env.example 已配置正确的默认值
- [ ] requirements.txt 包含所有必要的依赖
- [ ] render.yaml 配置文件已准备
- [ ] OPENROUTER_API_KEY 已获取
- [ ] 本地测试通过 (python test_full.py)

## 🔍 部署后验证

1. 访问部署的应用 URL
2. 检查 `/health` 端点是否返回 `{"status": "ok"}`
3. 上传一个小的 PDF 文件进行测试
4. 验证翻译功能是否正常工作

## 📝 常见问题

### 部署失败

- 检查 Render 的构建日志
- 确保 requirements.txt 中的所有依赖都兼容
- 检查 Python 版本是否为 3.8+

### 应用超时

- 增加 Render 的实例类型
- 检查 API 调用是否超时
- 增加 httpx 的超时时间

### 文件上传失败

- 检查 uploads 和 output 目录权限
- 确保磁盘空间充足
- 检查文件大小限制 (MAX_FILE_SIZE = 50MB)

## 🔐 安全建议

1. 不要在代码中硬编码 API Key
2. 使用 Render 的环境变量管理敏感信息
3. 定期更新依赖包
4. 监控 API 使用量和成本

## 📞 支持

如有问题，请检查：
- Render 的构建和运行日志
- OpenRouter API 文档
- Flask 官方文档
