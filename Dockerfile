FROM python:3.11-slim

# 安装必要的系统依赖
# build-essential: 编译工具
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 设置环境变量
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["gunicorn", "app.main:app", "-b", "0.0.0.0:8080", "--timeout", "180", "--workers", "2"]
