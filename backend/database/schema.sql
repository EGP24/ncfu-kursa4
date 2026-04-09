CREATE TABLE IF NOT EXISTS users (
    id              SERIAL                    PRIMARY KEY,       -- Уникальный идентификатор пользователя
    username        VARCHAR                   UNIQUE NOT NULL,   -- Уникальное имя пользователя
    password_hash   VARCHAR                   NOT NULL,          -- Хэш пароля для безопасного хранения
    created_at      TIMESTAMP WITH TIME ZONE  NOT NULL           -- Дата и время создания пользователя
);

CREATE TABLE IF NOT EXISTS lists (
    id              SERIAL                    PRIMARY KEY,      -- Уникальный идентификатор списка
    title           VARCHAR                   NOT NULL,         -- Название списка
    owner_id        BIGINT                    NOT NULL,         -- Идентификатор владельца списка
    share_token     VARCHAR                   UNIQUE,           -- Уникальный токен для доступа к списку
    is_deleted      BOOLEAN                   NOT NULL,         -- Статус удаления списка
    created_at      TIMESTAMP WITH TIME ZONE  NOT NULL,         -- Дата и время создания списка
    updated_at      TIMESTAMP WITH TIME ZONE  NOT NULL,         -- Дата и время обновления списка
    CONSTRAINT lists_owner_id_fk FOREIGN KEY(owner_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS items (
    id              SERIAL                         PRIMARY KEY,     -- Уникальный идентификатор элемента
    list_id         BIGINT                         NOT NULL,        -- Идентификатор списка, к которому принадлежит элемент
    name            VARCHAR                        NOT NULL,        -- Название элемента
    quantity        NUMERIC(10, 2)                 NOT NULL,        -- Количество элемента
    unit            VARCHAR,                                        -- Единица измерения элемента
    checked         BOOLEAN                        NOT NULL,        -- Статус выполнения элемента (отмечен/не отмечен)
    position        BIGINT                         NOT NULL,        -- Позиция элемента в списке для сортировки
    manual_position BIGINT                     NOT NULL,        -- Ручная позиция элемента в списке
    is_deleted      BOOLEAN                        NOT NULL,        -- Статус удаления элемента
    created_at      TIMESTAMP WITH TIME ZONE       NOT NULL,        -- Дата и время создания элемента
    updated_at      TIMESTAMP WITH TIME ZONE       NOT NULL,        -- Дата и время обновления элемента
    CONSTRAINT items_list_id_fk FOREIGN KEY(list_id) REFERENCES lists(id)
);

CREATE TABLE IF NOT EXISTS list_history (
    id          SERIAL                    PRIMARY KEY,  -- Уникальный идентификатор записи истории
    list_id     BIGINT                    NOT NULL,     -- Идентификатор списка, к которому относится запись истории
    action      VARCHAR                   NOT NULL,     -- Действие, которое произошло
    item_id     BIGINT                    NOT NULL,     -- Идентификатор элемента
    details     TEXT,                                   -- Дополнительные детали о действии
    actor_id    BIGINT,                                 -- Идентификатор пользователя, который совершил действие
    created_at  TIMESTAMP WITH TIME ZONE  NOT NULL,     -- Дата и время создания записи истории
    CONSTRAINT list_history_list_id_fk FOREIGN KEY(list_id) REFERENCES lists(id),
    CONSTRAINT list_history_item_id_fk FOREIGN KEY(item_id) REFERENCES items(id),
    CONSTRAINT list_history_actor_id_fk FOREIGN KEY(actor_id) REFERENCES users(id)
);
