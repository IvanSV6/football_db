import os
from dotenv import load_dotenv
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox
from controllers.session import session

load_dotenv()

class AutorizDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")
        self.setFixedSize(300, 250)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.label = QLabel("Выберите режим входа:")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.btn_admin = QPushButton("Вход как Админ")
        self.btn_admin.clicked.connect(lambda: self.check_access("admin"))
        layout.addWidget(self.btn_admin)

        self.btn_manager = QPushButton("Вход как Менеджер")
        self.btn_manager.clicked.connect(lambda: self.check_access("manager"))
        layout.addWidget(self.btn_manager)

    def check_access(self, role):
        entered_pass = self.password_input.text()
        env_key = "ADMIN_PASSWORD" if role == "admin" else "MANAGER_PASSWORD"
        correct_pass = os.getenv(env_key)

        print(f"DEBUG: Role={role}, Correct Pass={correct_pass}")

        if entered_pass == correct_pass and correct_pass is not None:
            session.current_role = role
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка доступа", "Неверный пароль")
