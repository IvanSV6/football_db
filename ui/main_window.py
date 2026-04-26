from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QDialog

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
        self.autoriz_button = QPushButton("Войти")
        self.autoriz_button.setFixedSize(80, 25)
        self.autoriz_button.setFlat(True)
        self.autoriz_button.clicked.connect(self.handle_login)
        self.tabs.setCornerWidget(self.autoriz_button, Qt.Corner.TopRightCorner)

        self.init_tabs()

    def handle_login(self):
        dialog = AutorizDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            role_names = {
                "admin": "Админ",
                "manager": "Менеджер",
                "user": "Болельщик"
            }
            current_role_name = role_names.get(session.current_role, "user")
            self.autoriz_button.setText(f"Выйти ({current_role_name})")
            while self.tabs.count() > 0:
                self.tabs.removeTab(0)
            self.init_tabs()

    def init_tabs(self):
        if session.current_role == "admin" or session.current_role == "manager":
            for table_key in TABLE_CONFIG.keys():
                tab_title = TABLE_CONFIG[table_key]["title"]
                tab_widget = GenericTableTab(table_key)
                self.tabs.addTab(tab_widget, tab_title)
        elif session.current_role == "user":
            self.tournament_tab = TournamentTable()
            self.matches_tab = MatchesTab()
            self.teams_tab = TeamsTab()
            self.players_tab = PlayersTab()
            self.ranking_tab = RankingTab()
            self.tabs.addTab(self.tournament_tab, "Турнирная таблица")
            self.tabs.addTab(self.matches_tab, "Календарь матчей")
            self.tabs.addTab(self.teams_tab, "Клубы")
            self.tabs.addTab(self.players_tab,"Игроки")
            self.tabs.addTab(self.ranking_tab, "Статистика игроков")

