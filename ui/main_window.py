from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QDialog,QMessageBox

from ui.tabs.players import PlayersTab
from ui.tabs.ranking import RankingTab
from ui.tabs.tournament import TournamentTable
from ui.tabs.matches import MatchesTab
from ui.tabs.teams import TeamsTab
from config import TABLE_CONFIG
from ui.tabs.base_tab import GenericTableTab
from controllers.session import session
from ui.autoriz_form import AutorizDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Футбольные чемпионаты")
        self.resize(1200, 660)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.admin_view_mode = "admin"

        self.corner_widget = QWidget()
        self.corner_layout = QHBoxLayout(self.corner_widget)
        self.corner_layout.setContentsMargins(0, 0, 0, 0)
        self.corner_layout.setSpacing(10)

        self.btn_toggle_view = QPushButton("Перейти в режим пользователя")
        self.btn_toggle_view.setFlat(True)
        self.btn_toggle_view.setStyleSheet("color: #1976D2; font-weight: bold;")
        self.btn_toggle_view.clicked.connect(self.toggle_view)
        self.btn_toggle_view.hide()

        self.autoriz_button = QPushButton("Войти")
        self.autoriz_button.setFixedSize(120, 25)
        self.autoriz_button.clicked.connect(self.handle_login)

        self.corner_layout.addWidget(self.btn_toggle_view)
        self.corner_layout.addWidget(self.autoriz_button)

        self.tabs.setCornerWidget(self.corner_widget, Qt.Corner.TopRightCorner)

        self.init_tabs()

    def handle_login(self):
        if session.current_role != "user":
            reply = QMessageBox.question(self, 'Выход', 'Вы действительно хотите выйти?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
            session.logout()
            self.autoriz_button.setText("Войти")
            self.btn_toggle_view.hide()
            self.admin_view_mode = "user"
            self.reload_tabs()
            return
        dialog = AutorizDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.autoriz_button.setText("Выйти")
            if session.current_role == "admin":
                self.admin_view_mode = "admin"
                self.btn_toggle_view.setText("Режим пользователя")
                self.btn_toggle_view.show()
            else:
                self.btn_toggle_view.hide()
            self.reload_tabs()

    def toggle_view(self):
        if self.admin_view_mode == "admin":
            self.admin_view_mode = "user"
            self.btn_toggle_view.setText("admin-панель")
        else:
            self.admin_view_mode = "admin"
            self.btn_toggle_view.setText("Режим пользователя")
        self.reload_tabs()

    def reload_tabs(self):
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)
        self.init_tabs()

    def init_tabs(self):
        is_admin_crud_mode = (session.current_role == "admin" and self.admin_view_mode == "admin")

        if is_admin_crud_mode:
            for table_key in TABLE_CONFIG.keys():
                tab_title = TABLE_CONFIG[table_key]["title"]
                tab_widget = GenericTableTab(table_key)
                self.tabs.addTab(tab_widget, tab_title)
        else:
            self.tournament_tab = TournamentTable()
            self.matches_tab = MatchesTab()
            self.teams_tab = TeamsTab()
            self.players_tab = PlayersTab()
            self.ranking_tab = RankingTab()

            self.tabs.addTab(self.tournament_tab, "Турнирная таблица")
            self.tabs.addTab(self.matches_tab, "Календарь матчей")
            self.tabs.addTab(self.teams_tab, "Клубы")
            self.tabs.addTab(self.players_tab, "Игроки")
            self.tabs.addTab(self.ranking_tab, "Статистика игроков")