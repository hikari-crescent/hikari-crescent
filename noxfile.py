from __future__ import annotations

import functools
import typing

import nox


def poetry_session(
    *groups: str, extras: bool = False, **kwargs: typing.Any
) -> typing.Callable[[typing.Callable[[nox.Session], None]], typing.Callable[[nox.Session], None]]:
    def inner(
        callback: typing.Callable[[nox.Session], None]
    ) -> typing.Callable[[nox.Session], None]:
        @nox.session(**kwargs)
        @functools.wraps(callback)
        def inner(session: nox.Session) -> None:
            session.install("poetry")
            session.run("poetry", "shell")

            command = ["poetry", "install"]

            if groups:
                command += ["--with=" + ",".join(groups)]

            if extras:
                command += ["--all-extras"]

            session.run(*command)

            callback(session)

        return inner

    return inner


@poetry_session("linting", name="format")
def apply_lint(session: nox.Session) -> None:
    session.run("black", "crescent")
    session.run("isort", "crescent")
    session.run("codespell", "crescent", "-i", "2", "-w")
    session.run("codespell", "docs", "-i", "2", "-w")


@poetry_session("linting")
def lint(session: nox.Session) -> None:
    session.run("black", "--check", "crescent")
    session.run("codespell", "crescent")
    session.run("codespell", "docs")
    session.run("ruff", "crescent")
    session.run("isort", "--check", "crescent")


@poetry_session("typing", extras=True)
def mypy(session: nox.Session) -> None:
    session.run("poetry", "run", "mypy", "crescent")


@poetry_session("typing", extras=True)
def pyright(session: nox.Session) -> None:
    session.run("poetry", "run", "pyright")
    session.run("poetry", "run", "pyright", "--verifytypes", "crescent")


@poetry_session("tests")
def pytest(session: nox.Session) -> None:
    session.install("hikari[server]")
    session.run("poetry", "run", "pytest", "tests/crescent", "--cov=crescent/")


@poetry_session("doc")
def docs(session: nox.Session) -> None:
    session.run("poetry", "run", "mkdocs", "-q", "build")


@poetry_session("doc")
def servedocs(session: nox.Session) -> None:
    session.run("poetry", "run", "mkdocs", "serve")
