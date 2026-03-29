import importlib.util
from pathlib import Path

import pytest


def test_get_env_raises_for_required_missing(monkeypatch) -> None:
    # Arrange
    config = _reload_config_with_env(
        monkeypatch,
        DATABASE_URL='postgresql://db',
        JWT_SECRET='x' * 32,
    )

    # Act & Assert
    with pytest.raises(RuntimeError, match='Environment variable MISSING is required'):
        config._get_env('MISSING', required=True)


def test_build_database_url_prefers_database_url_env(monkeypatch) -> None:
    # Arrange
    config = _reload_config_with_env(
        monkeypatch,
        DATABASE_URL='postgresql://ready-url',
        JWT_SECRET='x' * 32,
    )

    # Act
    result = config._build_database_url()

    # Assert
    assert result == 'postgresql://ready-url'


def test_build_database_url_constructs_from_postgres_parts(monkeypatch) -> None:
    # Arrange
    config = _reload_config_with_env(
        monkeypatch,
        POSTGRES_USER='user',
        POSTGRES_PASSWORD='pass',
        POSTGRES_DB='db',
        POSTGRES_HOST='127.0.0.1',
        POSTGRES_PORT='5433',
        JWT_SECRET='x' * 32,
    )

    # Act
    result = config._build_database_url()

    # Assert
    assert result == 'postgresql://user:pass@127.0.0.1:5433/db'


def test_config_module_uses_defaults_for_host_and_port(monkeypatch) -> None:
    # Arrange & Act
    config = _reload_config_with_env(
        monkeypatch,
        DATABASE_URL='postgresql://ready-url',
        JWT_SECRET='x' * 32,
        HOST=None,
        PORT=None,
    )

    # Assert
    assert config.HOST == '0.0.0.0'
    assert config.PORT == 8080


def _reload_config_with_env(monkeypatch, **env: str | None):
    for key in (
        'DATABASE_URL',
        'POSTGRES_USER',
        'POSTGRES_PASSWORD',
        'POSTGRES_DB',
        'POSTGRES_HOST',
        'POSTGRES_PORT',
        'JWT_SECRET',
        'HOST',
        'PORT',
    ):
        monkeypatch.delenv(key, raising=False)

    for key, value in env.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)

    config_path = Path(__file__).resolve().parents[1] / 'config.py'
    spec = importlib.util.spec_from_file_location('_test_config_module', config_path)
    if spec is None or spec.loader is None:
        raise RuntimeError('Failed to load config module spec')

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
