from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from ui.tabs.tournament import TournamentTable
from ui.tabs.matches import MatchesTable
from config import TABLE_CONFIG
from ui.tabs.base_tab import GenericTableTab

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
        for table_key in TABLE_CONFIG.keys():
            tab_title = TABLE_CONFIG[table_key]["title"]
            tab_widget = GenericTableTab(table_key)
            self.tabs.addTab(tab_widget, tab_title)