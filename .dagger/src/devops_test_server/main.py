from typing import Annotated

import dagger
from dagger import DefaultPath, Doc, Ignore, dag, function, object_type

SOURCE_IGNORE = [".git", ".dagger", ".venv", "venv", "__pycache__", ".pytest_cache", "*.db"]

# 可选参数：国内网络下本地运行时，用它把 pip 指向国内镜像源。默认为空，即使用官方 PyPI。
PipIndexUrl = Annotated[
    str,
    Doc("pip 镜像源地址，例如 https://mirrors.aliyun.com/pypi/simple/ ；留空则用官方 PyPI"),
]


@object_type
class DevopsTestServer:
    def python(self, pip_index_url: str) -> dagger.Container:
        """python:3.12-slim 基础容器；传了镜像源就设置 PIP_INDEX_URL。"""
        ctr = dag.container().from_("python:3.12-slim")
        if pip_index_url:
            ctr = ctr.with_env_variable("PIP_INDEX_URL", pip_index_url)
        return ctr

    @function
    async def lint(
        self,
        source: Annotated[dagger.Directory, DefaultPath("/"), Ignore(SOURCE_IGNORE)],
        pip_index_url: PipIndexUrl = "",
    ) -> str:
        """静态检查：ruff check 查代码问题，ruff format --check 查格式（规则在 ruff.toml）。"""
        return await (
            self.python(pip_index_url)
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
        source: Annotated[dagger.Directory, DefaultPath("/"), Ignore(SOURCE_IGNORE)],
        pip_index_url: PipIndexUrl = "",
    ) -> str:
        """在 python:3.12-slim 容器里安装依赖并运行 pytest -q。"""
        return await (
            self.python(pip_index_url)
            .with_directory("/app", source)
            .with_workdir("/app")
            .with_exec(["pip", "install", "--no-cache-dir", "-r", "requirements-dev.txt"])
            .with_exec(["pytest", "-q"])
            .stdout()
        )
