from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from ui.tabs.tournament import TournamentTable
from ui.tabs.matches import MatchesTable

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Футбольные чемпионаты")
        self.resize(1000, 550)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.init_tabs()

    def init_tabs(self):
        self.tournament_tab = TournamentTable()
        self.matches_tab = MatchesTable()
        self.clubs_tab = QWidget()
        self.players_tab = QWidget()
        self.stats_tab = QWidget()

        self.tabs.addTab(self.tournament_tab, "Турнирная таблица")
        self.tabs.addTab(self.matches_tab, "Календарь матчей")
        self.tabs.addTab(self.clubs_tab, "Клубы")
        self.tabs.addTab(self.players_tab, "Игроки")
        self.tabs.addTab(self.stats_tab, "Статистика")