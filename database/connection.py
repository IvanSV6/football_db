import psycopg2

class DatabaseConnection:
    def __init__(self):
        self.connection = None
    def get_connection(self):
        if self.connection is None or self.connection.closed != 0:
            try:
                self.connection = psycopg2.connect(host="localhost", port="5433", database="football_db", user="postgres", password="mysecretpassword")
                print("Успешное подключение к базе данных")
                return self.connection
            except Exception as error:
                print(f"Ошибка подключения к базе данных {error}")
                return None
    def close_connection(self):
        if self.connection is not None and self.connection.closed == 0:
            self.connection.close()
            print("Соединение с БД закрыто")


db = DatabaseConnection()
if __name__ == "__main__":
    connection = db.get_connection()