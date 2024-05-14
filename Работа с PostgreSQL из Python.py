"""
Олег извините, я два Ваших замечания не могу понять:

- при удалении клиентов стоит предусмотреть ситуацию, 
в которой к клиенту будут привязаны номера телефонов. 
В таком случае сразу клиента удалить не получится. (По моему изначально это предусмотренно)

- не стоит использовать f-строки или конкатенацию строк 
для формирования запросов, это небезопасно, т.к. 
открывает возможность для sql-инъекций (как я понял, что в f строки можно делать, 
главное переменые помещать в кортедж)
"""

import psycopg2

BASE = "Работа с PostgreSQL из Python"  # имя БД
PASSWORD = "postgres"  # пароль БД
USER = "postgres"


def connect(sql, params=(), b=BASE, p=PASSWORD, u=USER):
    """для sql запроса"""
    result = ""
    conn = psycopg2.connect(database=b, user=u, password=p)
    with conn.cursor() as cur:
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        if "RETURNING" in sql:
            result = cur.fetchone()
        elif "SELECT" in sql:
            result = cur.fetchall()
        conn.commit()
    conn.close()
    if result:
        return result


def create_BD():
    """Функция, создающая структуру БД (таблицы)"""
    connect(
        """
CREATE TABLE IF NOT EXISTS клиент (
id serial4 NOT NULL,
имя varchar NOT NULL,
фамилия varchar NOT NULL,
email varchar NOT NULL,
CONSTRAINT клиент_pk PRIMARY KEY (id));

CREATE TABLE IF NOT EXISTS телефон (
id_клиент int4 NOT NULL,
телефон varchar NOT NULL,
CONSTRAINT телефон_клиент_fk FOREIGN KEY (id_клиент) REFERENCES public.клиент(id));
"""
    )


def new_client(имя, фамилия, email, *телефон):
    """Функция, позволяющая добавить нового клиента"""
    if телефон:
        result = connect(
            "INSERT INTO клиент(имя, фамилия, email) VALUES (%s, %s, %s) RETURNING id;",
            (имя, фамилия, email),
        )[0]
        connect(
            f"INSERT INTO телефон VALUES {
                ", ".join("(%s, %s)" for t in телефон)};",
            tuple(r for t in телефон for r in (result, t)),
        )
    else:
        connect("INSERT INTO клиент(имя, фамилия, email) VALUES (%s, %s, %s);",
                (имя, фамилия, email))


def add_phone(id_client, телефон):
    """Функция, позволяющая добавить телефон для существующего клиента."""
    connect("INSERT INTO телефон VALUES (%s, %s);", (id_client, телефон))


def new_name_email(id_client, имя='', фамилия='', email=''):
    """Функция, позволяющая изменить данные о клиенте."""
    if имя or фамилия or email:
        text = []
        params = [имя, фамилия, email, id_client]
        text += ["имя = %s"] if имя else ""
        text += ["фамилия = %s"] if фамилия else ""
        text += ["email = %s"] if email else ""
        connect(f"UPDATE клиент SET {', '.join(
            text)} WHERE id = %s;", tuple(x for x in params if x))
    else:
        print("Вы не ввели параметры замены")


def delete_phone(id_client):
    """Функция, позволяющая удалить телефон для существующего клиента."""
    connect("DELETE FROM телефон WHERE id_клиент = %s;", (id_client, ))


def delete_client(id_client):
    """Функция, позволяющая удалить существующего клиента."""
    delete_phone(id_client)
    connect("DELETE FROM клиент WHERE id = %s;", (id_client, ))


def search(имя='', фамилия='', email='', телефон=''):
    """Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону."""
    поиск = []
    if имя:
        поиск.append('к.имя LIKE %s')
    if фамилия:
        поиск.append('к.фамилия LIKE %s')
    if email:
        поиск.append('к.email LIKE %s')
    if телефон:
        поиск.append('т.телефон LIKE %s')
    a = connect(f"""
SELECT к.id, к.имя, к.фамилия, к.email, т.телефон
FROM клиент к
LEFT JOIN телефон т ON к.id = т.id_клиент
WHERE {' AND '.join(поиск)};
""", tuple(f"%{x}%" for x in (имя, фамилия, email, телефон) if x))
    print(a)


if __name__ == "__main__":
    create_BD()
    new_client("vas9", "пупкин", "dfsfsd@dgdg", "634634636")
    new_client("йййййй", "yyyyyy", "sdgdgd@dsgdf", "634634636")
    new_client("ккккккк", "wwwwwwww", "sdgdgdf@dsgdgd",
               "635735735", "3572646547")
    add_phone("2", "777777777")
    new_name_email("1", "ееееееее", "mmmmmmmmm", "22222222@2222222")
    new_name_email("2", "nnnnnnnnnn")
    new_name_email("3", email="3333333@3333333")
    delete_phone("3")
    delete_client("1")
    search("nnnn")
    search("ккккк", "wwwww",)
    search("nnnn", '', '', '6346')
