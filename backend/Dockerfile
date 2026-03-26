FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.1.3 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

COPY backend/pyproject.toml backend/poetry.lock* ./
RUN poetry lock && poetry install --no-root --without dev

COPY backend/ ./

EXPOSE 8080

CMD ["python", "app.py"]
