# === 第一阶段：生成 requirements.txt ===
FROM python:3.10-slim as requirements-stage

WORKDIR /tmp

# 使用国内镜像安装 pip 和 poetry
RUN pip install --no-cache-dir --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir poetry -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制依赖文件
COPY ./pyproject.toml ./poetry.lock* /tmp/

# 导出 requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# === 第二阶段：最终运行镜像 ===
FROM python:3.10-slim

WORKDIR /srv/app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libffi-dev curl bash && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 复制 requirements 并安装
COPY --from=requirements-stage /tmp/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目代码
COPY . .

# 暴露端口
EXPOSE 80

# 默认启动命令（app）
CMD ["python", "manage.py", "run-prod-server"]