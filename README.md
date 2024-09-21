# TAXCOM


## Тестовое задание Python

1. Точка входа - main.py, запуск:

```python
python3 main.py
```

2. Не использовал внешние зависимости;
3. Понятно, что много чего можно улучшить - выделить все в соотв классы, создать кастомные исключения/улучшить обработку ошибок, читать/писать асинхронно, но будто бы в данный момент это избыточно;
4. Мною было принято решение, что сортировка необходима по названию item'а;
5. Тащить драйвера + orm-либы, описывать модели кажется также излишним. Поэтому для генерации чего-то в бд предлагаю ограничиться примерами запросов:

```sql
CREATE SCHEMA IF NOT EXISTS myawesomeschema;

CREATE TABLE myawesomeschema.items (
    item_uid UUID PRIMARY KEY,
    item_id BIGINT NOT NULL,
    item_name TEXT NOT NULL
);

INSERT INTO items (item_uid, item_id, item_name) VALUES
    ('e9adab35-9fc0-41a1-86e5-d16a2cf3d5ea', 123, 'Ветер'),
    ('468787f9-362e-4cf0-b22b-4fc3074e4cb7', 9, 'Ветка'),
    ('2581a221-0701-415c-83c8-b3a9c0a45ced', 4312, 'ЛОдка'),
    ('cab16f09-ea33-48cd-ada1-eb1c6b37f549', 0, 'Ноль без палочки'),
    ('0b0790ad-a0fd-4766-971e-1d55a219e885', 9834, 'Омуль, свежая'),
    ('577af4e8-31ac-45db-8ef4-cfe2d0741fcd', 98314, 'Стол, белый'),
    ('0ed995f6-e9e4-4392-aea5-d5728f87c5c3', 999, 'пїЅпїЅпїЅпїЅпїЅ'),
    ('186354a3-910f-4293-b6c0-45465e93e2da', 123, 'пїЅпїЅпїЅпїЅпїЅ'),
    ('90ea2aa6-5cfd-43df-8353-2c49342e40b8', 65445, 'пїЅпїЅпїЅпїЅпїЅ'),
    ('d2184f22-95d1-4c6d-a9d1-4fffab9397c9', 40, 'пїЅпїЅпїЅпїЅпїЅ');
```

Uid'ы можно генерировать на стороне python [uuid4](https://docs.python.org/3/library/uuid.html#uuid.uuid4), либо на стороне бд, для [pg](https://www.postgresql.org/docs/current/uuid-ossp.html):

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA IF NOT EXISTS myawesomeschema;

CREATE TABLE myawesomeschema.items (
    item_uid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_id BIGINT NOT NULL,
    item_name TEXT NOT NULL
);

INSERT INTO items (item_uid, item_id, item_name) VALUES
    (uuid_generate_v4(), 123, 'Ветер'),
    ...
    (uuid_generate_v4(), 40, 'пїЅпїЅпїЅпїЅпїЅ');
```
