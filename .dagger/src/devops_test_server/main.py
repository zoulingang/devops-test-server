from typing import Annotated

import dagger
from dagger import DefaultPath, Ignore, dag, function, object_type


@object_type
class DevopsTestServer:
    @function
    async def lint(
        self,
        source: Annotated[
            dagger.Directory,
            DefaultPath("/"),
            Ignore([".git", ".dagger", ".venv", "venv", "__pycache__", ".pytest_cache", "*.db"]),
        ],
    ) -> str:
        """静态检查：ruff check 查代码问题，ruff format --check 查格式（规则在 ruff.toml）。"""
        return await (
            dag.container()
            .from_("python:3.12-slim")
            .with_exec(["pip", "install", "--no-cache-dir", "ruff==0.17.2"])
            .with_directory("/app", source)
            .with_workdir("/app")
            .with_exec(["ruff", "check", "."])
            .with_exec(["ruff", "format", "--check", "."])
            .stdout()
        )

    @function
    async def test(
        self,
        source: Annotated[
            dagger.Directory,
            DefaultPath("/"),
            Ignore([".git", ".dagger", ".venv", "venv", "__pycache__", ".pytest_cache", "*.db"]),
        ],
    ) -> str:
        """在 python:3.12-slim 容器里安装依赖并运行 pytest -q。"""
        return await (
            dag.container()
            .from_("python:3.12-slim")
            .with_directory("/app", source)
            .with_workdir("/app")
            .with_exec(["pip", "install", "--no-cache-dir", "-r", "requirements-dev.txt"])
            .with_exec(["pytest", "-q"])
            .stdout()
        )
