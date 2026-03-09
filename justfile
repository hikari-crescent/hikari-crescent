set dotenv-load

lint:
    uv run codespell crescent
    uv run codespell docs
    uv run ruff check

mypy:
    uv run --all-extras --dev mypy .

pyright:
    uv run --all-extras --dev pyright
    uv run --all-extras --dev pyright --verifytypes crescent --ignoreexternal

test:
    uv run --all-extras --dev pytest tests/crescent

test-bot:
    uv run --all-extras --dev pytest tests/test_bot

docs:
    uv run --all-extras --dev mkdocs -q build

servedocs:
    uv run --all-extras --dev mkdocs serve
