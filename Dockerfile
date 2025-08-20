FROM python:3.10-slim

WORKDIR /srv/app

# 换掉apt-get的源
RUN sed -i 's@deb.debian.org@mirrors.cloud.tencent.com@g' /etc/apt/sources.list.d/debian.sources

# 更新包索引
RUN apt-get update

# 安装编译工具
RUN apt-get install -y --no-install-recommends build-essential libffi-dev

# 安装网络和工具依赖
RUN apt-get install -y --no-install-recommends curl bash

# 安装 Node.js 和 npm
RUN apt-get install -y --no-install-recommends nodejs npm

# 清理缓存
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 升级 pip
RUN pip install --no-cache-dir --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 Poetry
RUN pip install --no-cache-dir poetry -i https://pypi.tuna.tsinghua.edu.cn/simple

# 配置 Poetry
RUN poetry config virtualenvs.create false

# 安装项目依赖
RUN poetry install --without dev --no-interaction --no-ansi

# 安装额外依赖
RUN pip install --no-cache-dir honcho gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple

# 暴露端口
EXPOSE 80

# 默认启动命令（app）
CMD ["python", "manage.py", "run-prod-server"]