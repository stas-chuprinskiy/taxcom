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


## Бизнес процесс

Основные связанные сущности счета:
- Контрагенты (поставщик/покупатель)
- Товары / услуги

Приведу набросок нескольких таблиц:

```sql
CREATE SCHEMA IF NOT EXISTS myawesomeschema;


CREATE EXTENSION IF NOT EXISTS "uuid-ossp" with schema myawesomeschema;


-- Таблица контрагентов
CREATE TABLE myawesomeschema.counterparties (
    counterparty_uid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name character varying NOT NULL,
    abbreviated_name character varying,
    legal_address character varying NOT NULL,
    postal_address character varying NOT NULL,
    contacts jsonb DEFAULT '{}'::jsonb NOT NULL,
    inn bigint NOT NULL UNIQUE,
    cat bigint NOT NULL
)


-- Таблица айтемов
CREATE TABLE myawesomeschema.items (
    item_uid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title character varying NOT NULL,
    price bigint NOT NULL,
    descr character varying
)


CREATE TYPE payment_status AS ENUM ('NOT_PAID', 'PARTIALLY_PAID', 'FULLY_PAID');
CREATE TYPE dispatch_status AS ENUM ('NOT_DISPATCHED', 'PARTIALLY_DISPATCHED', 'FULLY_DISPATCHED');


-- Таблица счетов
CREATE TABLE myawesomeschema.bills (
    bill_uid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bill_number BIGINT NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    buyer_uid UUID NOT NULL REFERENCES myawesomeschema.counterparties (counterparty_uid) ON DELETE RESTRICT,
    supplier_uid UUID NOT NULL REFERENCES myawesomeschema.counterparties (counterparty_uid) ON DELETE RESTRICT,
    payment_basis character varying NOT NULL,
    payment_purpose character varying,
    payment_status payment_status NOT NULL DEFAULT 'NOT_PAID',
    dispatch_status dispatch_status NOT NULL default 'NOT_DISPATCHED'
);


-- Таблица связи счета и товара
CREATE TABLE myawesomeschema.bill_item_set (
    bill_uid UUID REFERENCES myawesomeschema.bills (bill_uid) ON DELETE RESTRICT,
    item_uid UUID REFERENCES myawesomeschema.items (item_uid) ON DELETE RESTRICT,
    amount bigint NOT null,
    PRIMARY KEY (bill_uid, item_uid)
);


CREATE INDEX items_title_idx ON myawesomeschema.items (title);
CREATE INDEX bills_bill_number_idx ON myawesomeschema.bills (bill_number);
```


Очевидно, что много чего важного есть еще: банковские счета контрагентов, раздельные каталоги товаров и услуг, связанные отгрузки, оплаты, документы и тд, однако в рамках тестового задания все не охватить. Намерено опускаю owner_id в каждой из таблиц, т.к. в контексте задачи создатель сущности не важен. Об индексах: индексы автоматически генерируются при указании различных констрейнтов, будь то PRIMARY KEY, UNIQUE, REFERENCE. Дополнительны созданы items_title_idx и bills_bill_number_idx. Намерено не были созданы индексы для myawesomeschema.bills.payment_status и myawesomeschema.bills.dispatch_status, т.к. текущая реализация предполагает ENUM с малым кол-вом значений. Также намерено не занимаюсь оптимизацией типов полей, описанием ограничений, например, длин character varying, проверок CHECK >= 0 для price, amount и тд.


Примеры запросов, решающих требуемые задачи:

```sql
-- Создание view (реестра) на последние 20 счетов
-- если будет важен тип счета, где мы или buyer_uid, или supplier_uid, появится доп условие
-- также в задаче есть "менеджер", выше писал об опущении owner_uid, на конечный запрос это
-- концептуально не повлияет, добавится один фильтр по owner_uid
CREATE VIEW myawesomeschema.recent_bills AS
	SELECT * 
	FROM myawesomeschema.bills 
	ORDER BY created_at DESC, bill_number DESC 
	LIMIT 20;


-- Пример запроса на получение счетов конкретного контрагента по маске в full_name
SELECT b.*
FROM
    myawesomeschema.bills b, myawesomeschema.counterparties c
WHERE
    b.buyer_uid = c.counterparty_uid AND c.full_name ilike '%рога и копыта%';


-- Пример запроса на получение неоплаченных но полностью отгруженных счетов
-- при этом считаем, что либо сами периодически ходим в АПИ бухгалтерии, либо
-- получаем колбеки и актуализируем payment_status и dispatch_status
SELECT
    b.*
FROM
    myawesomeschema.bills b
WHERE
    b.payment_status = 'NOT_PAID' AND b.dispatch_status = 'FULLY_DISPATCHED'
ORDER BY
    b.created_at DESC, b.bill_number DESC
LIMIT 10;
```

Приводить примеры фильтрации по created_at, supplier_uid и тд не вижу практического смысла, думаю концепт понятен.
