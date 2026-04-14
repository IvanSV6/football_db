import os
from dotenv import load_dotenv

load_dotenv()

class SessionManager:
    def __init__(self):
        self.current_role = "admin"

    def login(self, password):
        if password == os.getenv("ADMIN_PASSWORD"):
            self.current_role = "admin"
            return True
        elif password == os.getenv("MANAGER_PASSWORD"):
            self.current_role = "manager"
            return True

        return False
    def logout(self):
        self.current_role = "admin"

session = SessionManager()
