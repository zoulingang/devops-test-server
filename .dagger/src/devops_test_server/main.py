from typing import Annotated

import dagger
from dagger import DefaultPath, Ignore, dag, function, object_type


@object_type
class DevopsTestServer:
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
