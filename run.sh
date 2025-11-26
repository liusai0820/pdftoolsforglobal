#!/bin/bash

# PDF 处理工具 Web 应用启动脚本

echo "🚀 启动 PDF 处理工具 Web 应用..."

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "❌ 错误: 找不到 .env 文件"
    echo "请复制 .env.example 为 .env 并设置 OPENROUTER_API_KEY"
    exit 1
fi

# 检查依赖
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 安装依赖..."
    pip install -r requirements.txt
fi

# 创建必要的目录
mkdir -p uploads output

# 启动应用
echo "✅ 应用启动中..."
echo "📍 访问地址: http://localhost:5000"
echo ""

python3 app/main.py
