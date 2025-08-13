FROM python:3.10-slim

WORKDIR /srv/app

# 安装系统依赖和 Node.js
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libffi-dev curl bash nodejs npm && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装 Poetry 和项目依赖（Poetry 2.x）
RUN pip install --no-cache-dir --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir poetry -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    poetry config virtualenvs.create false && \
    poetry install --without dev --no-interaction --no-ansi && \
    pip install --no-cache-dir honcho gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple

# 暴露端口
EXPOSE 80

# 默认启动命令（app）
CMD ["python", "manage.py", "run-prod-server"]