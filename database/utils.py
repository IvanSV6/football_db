from functools import wraps
from database.connection import db
from psycopg2.extras import RealDictCursor

def db_op(commit=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            conn = db.get_connection()
            if not conn:
                return []

            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    result = func(cursor, *args, **kwargs)
                    if commit:
                        conn.commit()
                    return result
            except Exception as e:
                print(f"Ошибка БД в функции {func.__name__}: {e}")
                if commit:
                    conn.rollback()
                return []
            finally:
                db.close_connection()
        return wrapper
    return decorator