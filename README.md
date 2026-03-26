# 🛒 Shopping List — Веб-приложение для ведения списков покупок

Полнофункциональное веб-приложение с совместным редактированием в реальном времени.

## Стек технологий

| Слой       | Технология                          |
|------------|-------------------------------------|
| Backend    | Python 3.13, aiohttp, asyncpg, Poetry, uv |
| Frontend   | JavaScript, React 18, Webpack        |
| Infra      | Docker, Docker Compose, Nginx         |
| База данных| PostgreSQL                           |
| Реалтайм   | WebSocket (aiohttp / браузерный API) |

## Функционал

- Регистрация и авторизация (JWT)
- Создание, просмотр, переименование и удаление списков покупок
- Добавление, редактирование и удаление пунктов списка (название, количество, единица измерения)
- Отметка пунктов как купленных (зачёркивание)
- Шаринг списков — генерация публичной ссылки, доступной без авторизации
- Совместное редактирование на WebSocket — все изменения отображаются в реальном времени у всех участников
- История изменений — кто, когда и что изменил в списке

## Структура проекта

```
kursa4-2/
├── .env.example             # Шаблон переменных окружения
├── .env                     # Локальные секреты (не коммитится)
├── Makefile                 # Общие команды для backend/frontend
├── docker-compose.yml       # Оркестрация всех сервисов
├── Dockerfile.nginx         # Сборка frontend + Nginx runtime
├── docker/
│   ├── nginx/
│   │   └── default.conf     # Nginx (SPA + reverse proxy /api)
│   └── postgres-data/       # Данные PostgreSQL на хосте
├── backend/
│   ├── app.py              # Точка входа сервера
│   ├── config.py            # Конфигурация (из .env)
│   ├── db.py                # Инициализация БД и миграции
│   ├── auth.py              # JWT-авторизация, хэширование паролей
│   ├── Makefile             # Команды для запуска и проверок
│   ├── Dockerfile           # Контейнер backend
│   ├── pyproject.toml       # Poetry-конфигурация и зависимости
│   ├── poetry.lock          # Зафиксированные версии зависимостей
│   ├── poetry.toml          # Настройки Poetry (venv в ./.venv)
│   └── routes/
│       ├── user_routes.py   # Регистрация, логин
│       ├── list_routes.py   # CRUD списков, шаринг, история
│       ├── item_routes.py   # CRUD пунктов списка
│       └── ws_routes.py     # WebSocket-подключение
└── frontend/
    ├── package.json         # npm-зависимости и скрипты
    ├── webpack.config.js    # Конфигурация Webpack
    ├── .babelrc             # Конфигурация Babel
    ├── public/
    │   └── index.html       # HTML-шаблон
    └── src/
        ├── index.js         # Точка входа React
        ├── App.js           # Роутинг, layout
        ├── api.js           # API-клиент + WebSocket
        ├── AuthContext.js   # Контекст авторизации
        ├── styles.css       # Стили
        ├── components/
        │   ├── Header.js       # Шапка приложения
        │   ├── ItemRow.js      # Строка пункта списка
        │   └── HistoryPanel.js # Панель истории изменений
        └── pages/
            ├── LoginPage.js       # Страница входа
            ├── RegisterPage.js    # Страница регистрации
            ├── ListsPage.js       # Список всех списков
            ├── ListDetailPage.js  # Детальная страница списка
            └── SharedListPage.js  # Страница расшаренного списка
```

---

## Запуск проекта

### Предварительные требования

- Для запуска в Docker: **Docker** и **Docker Compose**
- Для локального запуска без Docker: **Python 3.13**, **Poetry**, **uv**, **Node.js 16+**, **PostgreSQL**

## Запуск через Docker (backend + frontend + nginx + db)

```bash
cd kursa4-2

# Создать локальный .env из шаблона
cp .env.example .env

# Заполнить секреты и параметры окружения
nano .env

# Собрать и запустить все сервисы
make docker-up
```

После запуска:

- Приложение: `http://localhost`
- API через Nginx: `http://localhost/api/*`
- PostgreSQL: `localhost:5432`

Данные базы хранятся вне контейнера в директории `docker/postgres-data`, поэтому сохраняются между перезапусками.

Схема БД накатывается автоматически отдельным Docker-сервисом `migrate` из файла `backend/database/schema.sql`.

Перед деплоем измени `JWT_SECRET` и креды PostgreSQL в `.env`.

Полезные команды:

```bash
make docker-logs
make docker-down
```

---

## Локальный запуск без Docker

### 1. Клонирование / переход в директорию проекта

```bash
cd kursa4-2
```

### 2. Создание базы данных PostgreSQL

```bash
createdb shoplist_app
```

### 3. Накатить схему БД (для локального запуска)

```bash
psql postgresql://<ваш_пользователь>@localhost/shoplist_app -f backend/database/schema.sql
```

> Если PostgreSQL требует пароль, используй URL вида `postgresql://user:password@localhost:5432/shoplist_app`.

### 4. Настройка переменных окружения

Создайте `.env` из шаблона и отредактируйте его под свою конфигурацию PostgreSQL:

```bash
cp .env.example .env
nano .env
```

```dotenv
POSTGRES_DB=shoplist_app
POSTGRES_USER=<ваш_пользователь>
POSTGRES_PASSWORD=<пароль_пользователя>
JWT_SECRET=super-secret-key-change-in-production
HOST=0.0.0.0
PORT=8080
```

- `<ваш_пользователь>` — имя пользователя PostgreSQL (обычно совпадает с системным).
- `DATABASE_URL` можно не задавать: backend соберет его автоматически из `POSTGRES_*`.

### 5. Установка и запуск бэкенда (Poetry + uv)

```bash
# Установить Poetry (если ещё не установлен)
curl -sSL https://install.python-poetry.org | python3 -

# Установить uv (если ещё не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Полная настройка backend (Python 3.13 + локальная .venv + зависимости)
cd kursa4-2
make backend-setup

# Запуск сервера
make backend-run
```

Бэкенд запустится на **http://localhost:8080**.

`make backend-setup` делает следующее: устанавливает Python 3.13 через `uv`, создает локальное окружение `backend/.venv` через Poetry и устанавливает зависимости из `backend/pyproject.toml`.

#### Общие команды из корня проекта

```bash
cd kursa4-2
make backend-setup
make backend-run
make backend-check
make frontend-install
make frontend-run
```

#### Основные команды backend

```bash
cd backend
make setup
make run       # запустить сервер
make lint      # проверить стиль
make typecheck # проверить типы
make check     # lint + typecheck
```

#### Проверка кода (опционально)

Для проверки типов и стиля используйте:

```bash
make lint
make typecheck
# или обе проверки сразу
make check
```

### 6. Установка и запуск фронтенда

Откройте **новый терминал**:

```bash
cd kursa4-2
make frontend-install
make frontend-run
```

Фронтенд запустится на **http://localhost:3000** и автоматически откроется в браузере.

> Webpack dev server проксирует все запросы `/api/*` на бэкенд (порт 8080), включая WebSocket-соединения.

### 7. Готово!

Откройте **http://localhost:3000** в браузере.

---

## Сборка фронтенда для продакшена

```bash
cd kursa4-2
make frontend-build
```

Собранные файлы появятся в `frontend/dist/`.

---

## API-эндпоинты

### Авторизация

| Метод | URL                  | Описание           |
|-------|----------------------|---------------------|
| POST  | `/api/auth/register` | Регистрация         |
| POST  | `/api/auth/login`    | Вход                |

### Списки

| Метод  | URL                          | Описание                      |
|--------|------------------------------|-------------------------------|
| GET    | `/api/lists`                 | Все списки пользователя       |
| POST   | `/api/lists`                 | Создать список                |
| GET    | `/api/lists/:id`             | Получить список с пунктами    |
| PUT    | `/api/lists/:id`             | Переименовать список          |
| DELETE | `/api/lists/:id`             | Удалить список                |
| POST   | `/api/lists/:id/share`       | Сгенерировать ссылку шаринга  |
| DELETE | `/api/lists/:id/share`       | Отключить шаринг              |
| GET    | `/api/lists/:id/history`     | История изменений списка      |

### Пункты списка

| Метод  | URL                                  | Описание              |
|--------|--------------------------------------|-----------------------|
| POST   | `/api/lists/:id/items`               | Добавить пункт        |
| PUT    | `/api/lists/:id/items/:item_id`      | Изменить пункт        |
| DELETE | `/api/lists/:id/items/:item_id`      | Удалить пункт         |

### Шаринг (без авторизации)

| Метод | URL                          | Описание                        |
|-------|------------------------------|---------------------------------|
| GET   | `/api/shared/:share_token`   | Получить расшаренный список     |

### WebSocket

| URL                              | Описание                         |
|----------------------------------|----------------------------------|
| `ws://localhost:8080/api/ws/:id` | Подключение к реалтайм-обновлениям списка |

Параметры подключения (query string): `token` (JWT) или `share_token`.
