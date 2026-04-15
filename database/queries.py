from database.connection import db
from psycopg2.extras import RealDictCursor
from psycopg2 import sql


def get_all_table(table):
    conn = db.get_connection()
    if not conn:
        return []

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = f"SELECT * FROM {table};"
            cursor.execute(query)
            result = cursor.fetchall()
            return result

    except Exception as e:
        print(f"Ошибка при получении данных из таблицы: {table}")
        return []

    finally:
        db.close_connection()


def insert_record(table, data):
    conn = db.get_connection()
    if not conn: return False
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            columns = data.keys()
            values = [data[col] for col in columns]

            query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values})").format(
                table=sql.Identifier(table),
                fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
                values=sql.SQL(', ').join(sql.Placeholder() * len(values))
            )
            cursor.execute(query, values)
            conn.commit()
            return True
    except Exception as e:
        print(f"Ошибка INSERT: {e}")
        conn.rollback()
        return False
    finally:
        db.close_connection()

def update_record(table, id_column, record_id, data):
    conn = db.get_connection()
    if not conn: return False
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            columns = data.keys()
            values = [data[col] for col in columns]
            values.append(record_id)

            set_clause = sql.SQL(', ').join(
                [sql.SQL("{} = %s").format(sql.Identifier(col)) for col in columns]
            )

            query = sql.SQL("UPDATE {table} SET {clause} WHERE {id_field} = %s").format(
                table=sql.Identifier(table),
                clause=set_clause,
                id_field=sql.Identifier(id_column)
            )
            cursor.execute(query, values)
            conn.commit()
            return True
    except Exception as e:
        print(f"Ошибка UPDATE: {e}")
        conn.rollback()
        return False
    finally:
        db.close_connection()

def delete_record(table, id_column, record_id):
    conn = db.get_connection()
    if not conn: return False
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = sql.SQL("DELETE FROM {table} WHERE {id_field} = %s").format(
                table=sql.Identifier(table),
                id_field=sql.Identifier(id_column)
            )
            cursor.execute(query, (record_id,))
            conn.commit()
            return True
    except Exception as e:
        print(f"Ошибка DELETE: {e}")
        conn.rollback()
        return False
    finally:
        db.close_connection()

if __name__ == "__main__":
    teams = get_all_table("teams")
    print(teams)
