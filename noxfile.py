import typing
import nox


def poetry_session(
    callback: typing.Callable[[nox.Session], None]
) -> typing.Callable[[nox.Session], None]:
    @nox.session(name=callback.__name__)
    def inner(session: nox.Session) -> None:
        session.install('poetry')
        session.run('poetry', 'shell')
        session.run('poetry', 'install')
        callback(session)

    return inner


@poetry_session
def flake8(session: nox.Session) -> None:
    session.run('flake8', 'crescent')


@poetry_session
def codespell(session: nox.Session) -> None:
    session.run('codespell', 'crescent')


@poetry_session
def mypy(session: nox.Session) -> None:
    session.run('mypy', 'crescent')


@poetry_session
def pytest(session: nox.Session) -> None:
    session.run('pytest', 'tests/crescent')


@poetry_session
def docs(session: nox.Session) -> None:
    session.run('pdoc', 'crescent', '-d', 'google', '-o', 'docs/_build')
