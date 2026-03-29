from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
SCHEMA_PATH = BACKEND_DIR / 'database' / 'schema.sql'
JWT_TEST_SECRET = 'test-secret'
