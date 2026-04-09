# Shopping List

Веб-приложение для ведения списков покупок с совместным редактированием в реальном времени.

## Что умеет приложение

- Регистрация и авторизация пользователей (JWT).
- Создание, редактирование и удаление списков покупок.
- Добавление, изменение, удаление и отметка товаров как купленных.
- Ручная сортировка drag-and-drop и автосортировка товаров.
- Публичный share-доступ по токену (без аккаунта).
- История изменений списка с фильтрами по типу действий.
- Реалтайм-обновления через WebSocket для всех подключенных участников.

## Технологии

| Слой | Стек |
|---|---|
| Backend | Python 3.13, aiohttp, asyncpg, SQLAlchemy Core, Poetry |
| Frontend | React 18, JavaScript, Webpack |
| Database | PostgreSQL 16 |
| Realtime | WebSocket |
| Infra | Docker, Docker Compose, Nginx |

## Архитектура сервисов

В Docker-режиме поднимаются 4 сервиса:

- `db` - PostgreSQL.
- `migrate` - одноразовое применение `backend/database/schema.sql`.
- `backend` - API сервер (`aiohttp`).
- `nginx` - раздача frontend и reverse proxy на backend (`/api/*` + WebSocket).

Порты по умолчанию:

- Приложение (Docker): `http://localhost`.
- Backend (локально без Docker): `http://localhost:8080`.
- Frontend dev server (локально без Docker): `http://localhost:3000`.
- PostgreSQL в Docker: `localhost:${POSTGRES_PUBLIC_PORT:-5432}`.

## Переменные окружения

Файл шаблона: `.env.example`.

| Переменная | Обязательна | По умолчанию | Описание |
|---|---|---|---|
| `POSTGRES_DB` | да | `shoplist_app` | Имя базы данных |
| `POSTGRES_USER` | да | `postgres` | Пользователь БД |
| `POSTGRES_PASSWORD` | да | `change-me` | Пароль пользователя БД |
| `POSTGRES_PUBLIC_PORT` | нет (Docker) | `5432` | Порт БД на хосте |
| `POSTGRES_HOST` | нет | `localhost` | Хост БД (локально) |
| `POSTGRES_PORT` | нет | `5432` | Порт БД (локально) |
| `DATABASE_URL` | нет | - | Если задан, имеет приоритет над `POSTGRES_*` |
| `JWT_SECRET` | да | `change-me-super-secret` | Секрет подписи JWT |
| `HOST` | нет | `0.0.0.0` | Хост backend |
| `PORT` | нет | `8080` | Порт backend |

Важно: перед продакшен-деплоем обязательно смените `JWT_SECRET` и креды PostgreSQL.

## Деплой в Docker (рекомендуется)

```bash
cp .env.example .env
nano .env
make docker-up
```

После запуска:

- Откройте `http://localhost`.
- API доступно через `http://localhost/api/*`.
- Данные PostgreSQL сохраняются в `docker/postgres-data`.

Полезные команды:

```bash
make docker-logs
make docker-build
make docker-down
```

## Локальный деплой без Docker

### 1) Подготовьте окружение

Нужно установить:

- Python 3.13
- `uv`
- Poetry
- Node.js 20+
- PostgreSQL 16+

Создайте `.env`:

```bash
cp .env.example .env
nano .env
```

### 2) Подготовьте PostgreSQL

Пример создания пользователя и БД:

```sql
CREATE USER shoplist_user WITH PASSWORD 'change-me';
CREATE DATABASE shoplist_app OWNER shoplist_user;
```

Примените схему:

```bash
psql -h localhost -p 5432 -U shoplist_user -d shoplist_app -f backend/database/schema.sql
```

### 3) Запустите backend

```bash
make backend-setup
make backend-run
```

Backend будет доступен на `http://localhost:8080`.

### 4) Запустите frontend

В отдельном терминале:

```bash
make frontend-install
make frontend-run
```

Frontend dev server: `http://localhost:3000`.

Webpack dev server проксирует `/api/*` и WebSocket на `http://localhost:8080`.

### Локальный production-вариант (без Docker)

1. Соберите frontend:

```bash
make frontend-install
make frontend-build
```

2. Запустите backend (`make backend-run`) как сервис (например, через systemd/supervisor).
3. Настройте Nginx, чтобы:
   - раздавать `frontend/dist`;
   - проксировать `/api/*` на `127.0.0.1:8080`;
   - проксировать WebSocket `/api/ws/*`.

Пример блока `server` (минимальный):

```nginx
server {
    listen 80;
    server_name _;

    root /absolute/path/to/kursa4/frontend/dist;
    index index.html;

    location /api/ {
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_pass http://127.0.0.1:8080;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## Команды Makefile

### Корневой `Makefile`

| Команда | Что делает |
|---|---|
| `make backend-setup` | Установка Python 3.13, создание `.venv`, установка backend-зависимостей |
| `make backend-lock` | Обновление `poetry.lock` backend |
| `make backend-install` | Установка backend-зависимостей |
| `make backend-run` | Запуск backend |
| `make backend-test` | Запуск unit + functional тестов backend |
| `make backend-lint` | Запуск Ruff для backend |
| `make backend-lint ARGS="--fix"` | Ruff с доп. аргументами |
| `make backend-typecheck` | Запуск mypy |
| `make backend-check` | `lint + typecheck` |
| `make frontend-install` | Установка frontend-зависимостей |
| `make frontend-run` | Запуск Webpack dev server |
| `make frontend-build` | Production build frontend |
| `make frontend-test` | Запуск Jest тестов frontend |
| `make frontend-e2e` | Запуск Cypress e2e тестов |
| `make frontend-all` | `install + test + build + e2e` |
| `make docker-up` | `docker compose up -d --build` |
| `make docker-down` | `docker compose down` |
| `make docker-logs` | Логи всех docker-сервисов |
| `make docker-build` | Пересборка docker-образов |

### `backend/Makefile`

| Команда | Что делает |
|---|---|
| `make -C backend setup` | Python 3.13 + Poetry env + установка зависимостей |
| `make -C backend lock` | Обновление lock-файла |
| `make -C backend install` | Установка зависимостей |
| `make -C backend run` | Запуск `python app.py` |
| `make -C backend test` | `pytest tests tests_functional` с coverage |
| `make -C backend lint` | `ruff check .` |
| `make -C backend typecheck` | `mypy .` |
| `make -C backend check` | `lint + typecheck` |

## Backend API

### Базовый URL

- Локально без Nginx: `http://localhost:8080/api`
- Через Docker/Nginx: `http://localhost/api`

### Авторизация

Поддерживаются 2 способа:

1. Заголовок `Authorization: Bearer <jwt>`
2. Cookie `kursa4_auth_token=<jwt>`

Для share-доступа используется query-параметр `share_token`.

### Форматы ответов и ошибок

- Успешные ответы - JSON.
- Стандартный ответ delete-операций: `{"ok": true}`.
- Ошибки валидации (`400`):

```json
{
  "error": "validation_error",
  "details": [
    {
      "message": "...",
      "instance_path": "/field"
    }
  ]
}
```

- Возможные текстовые ошибки: `Invalid credentials`, `Authentification required`, `Access denied`, `List not found`, `Item not found`, `Username already taken`.

### Эндпоинты

#### Auth

| Метод | Путь | Доступ | Описание |
|---|---|---|---|
| `POST` | `/api/auth/register` | public | Регистрация |
| `POST` | `/api/auth/login` | public | Логин |

`POST /api/auth/register` body:

```json
{
  "username": "alex",
  "password": "secret123"
}
```

Ответ (`register` и `login`):

```json
{
  "token": "<jwt>",
  "user": {
    "id": 1,
    "username": "alex"
  }
}
```

#### Lists

| Метод | Путь | Доступ | Описание |
|---|---|---|---|
| `GET` | `/api/lists` | JWT | Списки текущего пользователя |
| `POST` | `/api/lists` | JWT | Создать список |
| `GET` | `/api/lists/{list_id}` | JWT | Получить список с items |
| `PUT` | `/api/lists/{list_id}` | JWT | Переименовать список |
| `DELETE` | `/api/lists/{list_id}` | JWT | Удалить список |
| `POST` | `/api/lists/{list_id}/share` | JWT | Включить share-доступ |
| `DELETE` | `/api/lists/{list_id}/share` | JWT | Отключить share-доступ |
| `GET` | `/api/shared/{share_token}` | public | Получить список по share-токену |
| `GET` | `/api/lists/{list_id}/history` | JWT или `share_token` | История изменений |

Параметры `GET /api/lists/{list_id}/history`:

- `share_token` - токен общего доступа.
- `actions` - фильтр по действиям (можно передавать несколько):
  - `item_added`
  - `item_deleted`
  - `item_edited`
  - `item_checked`
  - `item_unchecked`

Пример:

```http
GET /api/lists/10/history?actions=item_added&actions=item_deleted
```

#### Items

| Метод | Путь | Доступ | Описание |
|---|---|---|---|
| `POST` | `/api/lists/{list_id}/items` | JWT или `share_token` | Добавить item |
| `PUT` | `/api/lists/{list_id}/items/{item_id}` | JWT или `share_token` | Обновить item |
| `DELETE` | `/api/lists/{list_id}/items/{item_id}` | JWT или `share_token` | Удалить item |
| `PUT` | `/api/lists/{list_id}/items/{item_id}/position` | JWT или `share_token` | Переместить item вручную |
| `PUT` | `/api/lists/{list_id}/items/sort` | JWT или `share_token` | Применить сортировку |

`POST /api/lists/{list_id}/items` body:

```json
{
  "name": "Milk",
  "quantity": 2,
  "unit": "l"
}
```

`PUT /api/lists/{list_id}/items/{item_id}` body (частичное обновление):

```json
{
  "name": "Milk 2%",
  "quantity": 1,
  "unit": "l",
  "checked": true
}
```

`PUT /api/lists/{list_id}/items/{item_id}/position` body:

```json
{
  "position": 0
}
```

`PUT /api/lists/{list_id}/items/sort` body:

```json
{
  "mode": "unchecked_first"
}
```

Режимы сортировки:

- `manual`
- `unchecked_first`
- `name_asc`

### WebSocket API

Подключение:

- Локально: `ws://localhost:8080/api/ws/{list_id}`
- Через Docker/Nginx: `ws://localhost/api/ws/{list_id}`

Параметры query:

- `token` - JWT (опционально, если есть cookie).
- `share_token` - share-токен (для гостевого доступа).

Клиент может отправлять `ping` (строка), сервер отвечает:

```json
{
  "type": "pong"
}
```

Типы server-сообщений:

- `item_added` (payload: `item`)
- `item_updated` (payload: `item`)
- `item_deleted` (payload: `item_id`)
- `history_updated`
- `pong`

## Деплой на сервер в Docker

Минимальный сценарий:

```bash
git clone <repo-url>
cd kursa4
cp .env.example .env
nano .env
make docker-up
```

Обновление приложения:

```bash
git pull
make docker-up
```

Остановка:

```bash
make docker-down
```

## CI/CD

В репозитории настроен workflow `.github/workflows/ci-cd.yml`:

- На PR/Push запускаются проверки backend и frontend.
- На push в `master` после успешных проверок выполняется деплой по SSH и `docker compose up -d --build --remove-orphans`.

## Структура проекта

```text
app/
├── backend/                # API, бизнес-логика, тесты
├── frontend/               # React-приложение
├── docker/nginx/           # Nginx-конфиг для SPA + /api proxy
├── docker-compose.yml      # Оркестрация сервисов
├── Dockerfile.nginx        # Сборка frontend + Nginx runtime
├── Makefile                # Основные команды проекта
└── .env.example            # Шаблон переменных окружения
```
