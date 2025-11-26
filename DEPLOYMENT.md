# 部署指南

## 本地开发环境

- [ ] Python 3.8+ 已安装
- [ ] 创建了 `.env` 文件（从 `.env.example` 复制）
- [ ] 设置了 `OPENROUTER_API_KEY`
- [ ] 运行 `pip install -r requirements.txt`
- [ ] 运行 `python test.py` 通过检查
- [ ] 运行 `python app/main.py` 成功启动
- [ ] 在浏览器中访问 http://localhost:5000 正常显示

## GitHub 准备

- [ ] 创建了 GitHub 仓库
- [ ] 初始化 Git: `git init`
- [ ] 添加所有文件: `git add .`
- [ ] 提交: `git commit -m "Initial commit"`
- [ ] 添加远程: `git remote add origin https://github.com/your-username/pdf-processor-web.git`
- [ ] 推送到 main 分支: `git push -u origin main`
- [ ] 验证文件已上传到 GitHub

## Render 部署

### 账户和权限

- [ ] 注册了 Render 账户 (https://render.com)
- [ ] 连接了 GitHub 账户到 Render
- [ ] 授予 Render 访问仓库的权限

### 创建 Web Service

- [ ] 在 Render Dashboard 点击 "New +" → "Web Service"
- [ ] 选择了正确的 GitHub 仓库
- [ ] 配置了以下设置：
  - [ ] Name: `pdf-processor`
  - [ ] Environment: `Python 3`
  - [ ] Build Command: `pip install -r requirements.txt`
  - [ ] Start Command: `gunicorn app.main:app`
  - [ ] Plan: Free (或付费)

### 环境变量配置

- [ ] 在 Render 中添加了 Secret 变量
- [ ] Key: `OPENROUTER_API_KEY`
- [ ] Value: 你的 OpenRouter API Key
- [ ] 验证了变量已保存

### 部署

- [ ] 点击 "Deploy" 按钮
- [ ] 等待构建完成（通常 2-5 分钟）
- [ ] 检查构建日志，确保没有错误
- [ ] 获得了部署 URL（例如：https://pdf-processor.onrender.com）

## 部署后验证

- [ ] 访问部署 URL，页面正常加载
- [ ] 上传一个 PDF 文件测试
- [ ] 测试 PDF 翻译功能
- [ ] 测试颜色替换功能
- [ ] 下载处理后的 PDF 文件
- [ ] 验证下载的文件可以正常打开

## 监控和维护

- [ ] 在 Render Dashboard 中设置了通知
- [ ] 定期检查应用日志
- [ ] 监控 API 使用情况
- [ ] 检查错误率和性能指标

## 文件结构检查

```
pdf-processor-web/
├── app/
│   └── main.py                 ✓
├── templates/
│   └── index_web.html          ✓
├── scripts/
│   ├── pdf_translator/         ✓
│   └── pdf_vector_color_replacer.py  ✓
├── uploads/                    ✓
├── output/                     ✓
├── requirements.txt            ✓
├── .env.example               ✓
├── .gitignore                 ✓
├── render.yaml                ✓
├── run.sh                     ✓
├── test.py                    ✓
├── README.md                  ✓
└── QUICK_START.md             ✓
```

## 常见问题

### 构建失败

1. 查看 Render 的构建日志
2. 检查 `requirements.txt` 中的依赖版本
3. 确保所有必要的文件都已提交到 GitHub
4. 尝试在本地重现问题

### 运行时错误

1. 检查 Render 的应用日志
2. 验证环境变量是否正确设置
3. 检查 API Key 是否有效
4. 查看是否有权限问题

### 功能不工作

1. 检查浏览器控制台的错误信息
2. 验证 API 端点是否正确
3. 检查文件上传是否成功
4. 查看后端日志中的详细错误

## 成本分析

### Render 成本

| 计划 | 月度成本 | 特点 |
|------|---------|------|
| Free | $0 | 750 小时/月，自动休眠 |
| Starter | $7 | 无限运行，基础性能 |
| Standard | $25 | 高性能，优先支持 |

### OpenRouter 成本

按 API 调用次数计费，具体价格取决于使用的模型。

## 下一步

1. **监控应用**：定期检查日志和性能指标
2. **收集反馈**：从用户那里获取使用反馈
3. **优化性能**：根据使用情况优化代码
4. **添加功能**：根据需求添加新功能
5. **扩展应用**：考虑添加更多 PDF 处理功能

---

**部署日期**：_____________

**部署人员**：_____________

**备注**：_____________
