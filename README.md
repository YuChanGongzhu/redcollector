# RedCollector

FastAPI service for interacting with Xiaohongshu (XHS): fetching posts, comments, and sending comments using stored cookies.


## Prerequisites

- `Python 3.9+`
- `Poetry 1.2+`
- `MySQL 5.7+ / 8.0+`
- `Redis 6+`
- `Node.js 16+` and `npm`


## Development

### Quick start

1) 配置环境变量（或 `.env` 文件）中的 Redis 和 MySQL 连接
2) 安装依赖

```shell
poetry install
```

3) 初始化数据库（首次）

```shell
poetry run aerich init-db
```

4) 启动后台任务 worker

```shell
poetry run python manage.py work
```

5) 安装前端依赖（进入 `app/xhs`）

```shell
cd app/xhs && npm install
```

6) 启动服务（FastAPI 工厂模式）

```shell
uvicorn app.main:get_application --factory --host 0.0.0.0 --port 8000 --reload
```

7) 打开接口文档： http://localhost:8000/docs

### `.env` example

```shell
DEBUG=True
SERVER_HOST=http://localhost:8000
SECRET_KEY=qwtqwubYA0pN1GMmKsFKHMw_WCbboJvdTAgM9Fq-UyM
SMTP_PORT=1025
SMTP_HOST=localhost
SMTP_TLS=False
BACKEND_CORS_ORIGINS=["http://localhost"]
DATABASE_URI=mysql://root:password@localhost:3306/redcollector
DEFAULT_FROM_EMAIL=RedCollector@gmail.com
REDIS_URL=redis://localhost:6379/0
FIRST_SUPERUSER_EMAIL=admin@mail.com
FIRST_SUPERUSER_PASSWORD=admin
```

### Database setup

Create your first migration

```shell
poetry run aerich init-db
```

Adding new migrations.

```shell
poetry run aerich migrate --name <migration_name>
```

Upgrading the database when new migrations are created.

```shell
poetry run aerich upgrade
```

### Run the fastapi app

```shell
poetry run python manage.py work
cd app/xhs && npm install
uvicorn app.main:get_application --factory --host 0.0.0.0 --port 8000 --reload
```

### Cli

There is a manage.py file at the root of the project, it contains a basic cli to hopefully
help you manage your project more easily. To get all available commands type this:

```shell
poetry run python manage.py --help
```

### Run the fastapi app with uvicorn

```shell
uvicorn app.main:get_application --factory --host 0.0.0.0 --port 8000 --reload
```
## Credits

This package was created with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [cookiecutter-fastapi](https://github.com/tobi-de/cookiecutter-fastapi) project template.
