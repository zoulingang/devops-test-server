# AGENTS.md

本文件是写给 AI 编码 Agent 的项目说明（[AGENTS.md 约定](https://agents.md/)）。面向人的介绍见 README.md，这里只写 Agent 动手前必须知道的事。

## 项目概况

- 极简 CRM 后端，**用于学习 CI/CD 和 E2E（基于 Dagger）**。保持最小：不要主动加框架、ORM、鉴权、新的 CI 阶段或部署流程，除非用户明确要求。
- Python 3.12 + FastAPI，存储用标准库 `sqlite3`（无 ORM）。代码只有 `app/main.py`（路由和模型）和 `app/db.py`（建表和连接）。
- 前端在另一个仓库 [devops-test-web](https://github.com/zoulingang/devops-test-web)，通过下面的 HTTP API 调用本服务。

## 常用命令

```bash
pip install -r requirements-dev.txt          # 安装依赖（建议先建 .venv）
uvicorn app.main:app --reload --port 8000    # 本地启动，文档在 /docs
pytest -q                                    # 单元测试（使用临时数据库）
ruff check . && ruff format --check .        # 代码检查和格式检查（ruff==0.17.2，规则在 ruff.toml）
ruff format .                                # 自动格式化
```

CI 跑的是 Dagger 函数，本地有 Dagger CLI（v0.21.11）和 Docker 时可以跑同样的命令：

```bash
dagger call lint
dagger call test
dagger call -m github.com/zoulingang/devops-test-web@main end-to-end --server=.
```

没有 Dagger 时，直接跑上面的 `pytest` 和 `ruff` 命令即可，结果等价。

## 提交前必须通过

1. `ruff check .` 和 `ruff format --check .` 无报错
2. `pytest -q` 全部通过
3. 改了 API、`Dockerfile` 或 `requirements.txt` 时，E2E 也要通过（见下）

## 修改 API 时的约束

- API 被前端页面（`devops-test-web/src/app.js`）和 E2E 用例同时使用：`/health`、`/api/customers` 的增删改查。**路径、字段名、状态码（新建 201、删除 204）不要随意改**。
- 改字段时要同时改三处：`app/db.py` 的建表语句、`app/main.py` 的 `FIELDS` 和 `CustomerIn`。新字段要可选，保证向后兼容。
- 为新接口或改动的行为在 `tests/test_api.py` 加测试。

## E2E 测试在哪里

- 本仓库**没有** E2E 用例。用例只有一份，在前端仓库的 `e2e/customers.spec.js`。
- 本仓库 CI 的 `end-to-end` job 调用前端仓库 main 分支的 Dagger 模块，用 `--server=.` 传入当前后端代码，并用本仓库的 `Dockerfile` 构建后端。
- 所以接口不兼容的改动会让 E2E 失败。需要前后端一起改时，要么保持向后兼容，要么临时把 `.github/workflows/ci.yml` 里的 `WEB_MODULE` 指向前端的对应分支。
- 只测 API、不需要浏览器的测试写在本仓库 `tests/`，用 pytest。

## CI 和 Dagger

- `.github/workflows/ci.yml` 有三个并行 job：`lint`、`test`、`end-to-end`，在 PR 上各自显示为一个检查。
- Dagger 模块在 `.dagger/src/devops_test_server/main.py`。函数名不要带数字（Dagger CLI 会把 `e2e` 变成 `e-2-e`）。
- 安装依赖的步骤放在拷贝源码之前，这样只改代码时能命中缓存。新增函数时保持这个顺序。
- Dagger 版本 0.21.11 同时写在 `dagger.json` 和 `ci.yml` 里，升级时一起改。
- `--pip-index-url` 参数只是为国内网络准备的，CI 里不要传。

## 约定

- 文档、注释、提交说明用中文；代码标识符用英文。
- 在分支上开发并提 PR，不要直接推 main。
- 不要提交 `crm.db`、`.venv/`、`.dagger/sdk/`、`.dagger/uv.toml`（已在 .gitignore 里）。
