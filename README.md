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

## Docker

```bash
docker build -t crm-server .
docker run -p 8000:8000 -v crm-data:/data crm-server
```
