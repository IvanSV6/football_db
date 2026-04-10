from database.connection import db
from psycopg2.extras import RealDictCursor


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


if __name__ == "__main__":
    teams = get_all_table("teams")
    print(teams)
