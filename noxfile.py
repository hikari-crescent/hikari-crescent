from __future__ import annotations

import typing

import nox


def poetry_session(
    callback: typing.Callable[[nox.Session], None]
) -> typing.Callable[[nox.Session], None]:
    @nox.session(name=callback.__name__)
    def inner(session: nox.Session) -> None:
        session.install("poetry")
        session.run("poetry", "shell")
        session.run("poetry", "install")
        callback(session)

    return inner


def pip_session(*args: str, name: str | None = None) -> typing.Callable[[nox.Session], None]:
    def inner(callback: typing.Callable[[nox.Session], None]):
        @nox.session(name=name or callback.__name__)
        def inner(session: nox.Session):
            for arg in args:
                session.install(arg)
            callback(session)

        return inner

    return inner


@pip_session("black", "isort", "codespell", name="apply-lint")
def apply_lint(session: nox.Session) -> None:
    session.run("black", "crescent")
    session.run("isort", "crescent")
    session.run("codespell", "crescent", "-i", "2")


@pip_session("flake8")
def flake8(session: nox.Session) -> None:
    session.run("flake8", "crescent")


@pip_session("codespell")
def codespell(session: nox.Session) -> None:
    session.run("codespell", "crescent")


@poetry_session
def mypy(session: nox.Session) -> None:
    session.run("poetry", "run", "mypy", "crescent")


@poetry_session
def pyright(session: nox.Session) -> None:
    session.run("poetry", "run", "pyright")
    session.run("poetry", "run", "pyright", "--verifytypes", "crescent")


@poetry_session
def pytest(session: nox.Session) -> None:
    session.run("poetry", "run", "pytest", "tests/crescent", "--cov=crescent/")


@poetry_session
def docs(session: nox.Session) -> None:
    session.run("pdoc", "crescent", "-d", "google", "-o", "docs/_build")
