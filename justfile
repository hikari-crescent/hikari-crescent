set dotenv-load

check:
    @just lint
    @just mypy
    @just pyright
    @just test
    @just docs

lint:
    uv run --dev codespell crescent
    uv run --dev codespell docs
    uv run --dev ruff check

mypy:
    uv run --dev --all-extras mypy crescent

pyright:
    uv run --dev pyright
    uv run --dev pyright --verifytypes crescent --ignoreexternal

test:
    uv run --dev pytest tests/crescent

test-bot:
    uv run --dev pytest tests/test_bot

docs:
    uv run --dev mkdocs -q build

servedocs:
    uv run --dev mkdocs serve
