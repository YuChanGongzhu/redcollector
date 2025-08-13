# 第一阶段：生成 requirements.txt
FROM python:3.10 as requirements-stage

WORKDIR /tmp

RUN pip install --no-cache-dir poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


# 第二阶段：最终运行镜像
FROM python:3.10-alpine

WORKDIR /srv/app

# 安装系统依赖
RUN apk update \
    && apk add --virtual build-deps build-base \
    && apk add --no-cache libffi-dev bash curl \
    && pip install --upgrade pip \
    && python --version

# 复制依赖清单并安装 Python 依赖
COPY --from=requirements-stage /tmp/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# 复制全部代码
COPY . .

# 默认端口
EXPOSE 80

# 默认启动命令（app）
CMD ["python", "manage.py", "run-prod-server"]