from PyQt6.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox
from controllers.session import session

class AutorizDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")
        self.setFixedSize(300, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Логин:"))
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        layout.addWidget(self.login_input)

        layout.addWidget(QLabel("Пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.btn_login = QPushButton("Войти")
        self.btn_login.clicked.connect(self.handle_login)
        self.btn_login.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        layout.addWidget(self.btn_login)

    def handle_login(self):
        login = self.login_input.text()
        password = self.password_input.text()

        if session.login(login, password):
            QMessageBox.information(self, "Успех", f"Вы вошли как {session.current_role}")
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль")