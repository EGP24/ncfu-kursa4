.PHONY: setup lock install run lint typecheck check

setup:
	uv python install 3.13
	poetry config --local virtualenvs.in-project true
	poetry env use "$$(uv python find 3.13)"
	poetry install

lock:
	poetry lock

install:
	poetry install

run:
	poetry run python app.py

lint:
	poetry run ruff check .

typecheck:
	poetry run mypy . --config-file pyproject.toml --explicit-package-bases

check: lint typecheck
