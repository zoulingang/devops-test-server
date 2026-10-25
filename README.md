# devops-test-server

极简 CRM 后端，用于学习 DevOps / CI/CD。前端在 [devops-test-web](https://github.com/zoulingang/devops-test-web)。

- 框架：**Python 3.12 + FastAPI**
- 存储：**SQLite**（Python 内置 `sqlite3`，无 ORM），首次启动自动建表
- 无鉴权、无角色

## 数据模型

`customers` 表：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | INTEGER | 主键，自增 |
| name | TEXT | 必填 |
| email / phone / company / notes | TEXT | 可选 |
| created_at | TEXT | 创建时间（UTC），自动生成 |

建表语句在 `app/db.py`，改字段时同时改 `app/main.py` 里的 `FIELDS` 和 `CustomerIn`。

## API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | 健康检查，返回 `{"status": "ok"}` |
| GET | `/api/customers` | 客户列表 |
| POST | `/api/customers` | 新建客户 |
| GET | `/api/customers/{id}` | 查看客户 |
| PUT | `/api/customers/{id}` | 修改客户 |
| DELETE | `/api/customers/{id}` | 删除客户 |

启动后可在 http://localhost:8000/docs 查看交互式文档。

## 本地运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

uvicorn app.main:app --reload --port 8000
```

数据库文件默认是当前目录下的 `crm.db`，可用环境变量 `CRM_DB_PATH` 修改。

## 测试

```bash
pytest -q
```

测试会使用临时数据库，不影响本地 `crm.db`。

## CI（Dagger）

CI 流程写在 Dagger 模块里，本地和 GitHub Actions 跑的是同一条命令：

```bash
dagger call lint   # 静态检查：ruff check + ruff format --check
dagger call test   # 单元测试：pytest -q
```

- `dagger.json`：模块声明（名字、Dagger 版本、用 Python SDK、代码在 `.dagger/`）
- `.dagger/src/devops_test_server/main.py`：两个函数。`lint` 在容器里装 ruff 做代码检查和格式检查（规则见 `ruff.toml`）；`test` 把代码放进 `python:3.12-slim` 容器，`pip install -r requirements-dev.txt` 后运行 `pytest -q`
- `.github/workflows/ci.yml`：在 PR 和 push 到 main 时先运行 `dagger call lint`，再运行 `dagger call test`

本地运行需要先安装 [Dagger CLI](https://docs.dagger.io/install)（v0.21.11）和 Docker。

在国内网络下访问 PyPI 很慢，可以给 `lint` / `test` 传一个镜像源（不传就用官方 PyPI，GitHub Actions 上就是不传）：

```bash
dagger call lint --pip-index-url=https://mirrors.aliyun.com/pypi/simple/
dagger call test --pip-index-url=https://mirrors.aliyun.com/pypi/simple/
```

Dagger 第一次加载模块时还要给 Python SDK 装依赖，这一步可以在 `.dagger/uv.toml` 里配置镜像源（该文件已被 git 忽略，只在本地生效）：

```toml
[[index]]
url = "https://mirrors.aliyun.com/pypi/simple/"
default = true
```

## 代码检查

```bash
pip install ruff==0.17.2
ruff check .          # 加 --fix 自动修复
ruff format .         # 自动格式化
```

## Docker

```bash
docker build -t crm-server .
docker run -p 8000:8000 -v crm-data:/data crm-server
```
