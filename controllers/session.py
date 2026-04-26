from database.queries import get_one


class SessionManager:
    def __init__(self):
        self.current_role = "user"  # По умолчанию гость
        self.user_data = None

    def login(self, login, password):
        user = get_one("users", "login", login)

        if user and user['password'] == password:
            self.user_data = user
            if user['access_level'] == 1:
                self.current_role = "admin"
            elif user['access_level'] == 2:
                self.current_role = "manager"
            return True
        return False

    def logout(self):
        self.current_role = "user"
        self.user_data = None

session = SessionManager()