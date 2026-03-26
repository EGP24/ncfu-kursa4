import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / '.env')


def _get_env(name: str, *, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and (value is None or value == ''):
        raise RuntimeError(f'Environment variable {name} is required')
    return value or ''


def _build_database_url() -> str:
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url

    user = _get_env('POSTGRES_USER', required=True)
    password = _get_env('POSTGRES_PASSWORD', required=True)
    db_name = _get_env('POSTGRES_DB', required=True)
    host = _get_env('POSTGRES_HOST', default='localhost')
    port = _get_env('POSTGRES_PORT', default='5432')

    return f'postgresql://{user}:{password}@{host}:{port}/{db_name}'


DATABASE_URL = _build_database_url()
JWT_SECRET = _get_env('JWT_SECRET', required=True)
HOST = _get_env('HOST', default='0.0.0.0')
PORT = int(_get_env('PORT', default='8080'))
