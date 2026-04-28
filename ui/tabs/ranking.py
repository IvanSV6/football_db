import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QLabel)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
from controllers.data_manager import data_manager


class RankingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_championships()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        top_layout = QHBoxLayout()
        title_lbl = QLabel("Статистика игроков")

        title_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #00bcd4;")

        self.combo_champ = QComboBox()
        self.combo_season = QComboBox()

        self.combo_champ.currentIndexChanged.connect(self.load_seasons)
        self.combo_season.currentIndexChanged.connect(self.refresh_all_tables)

        top_layout.addWidget(title_lbl)
        top_layout.addStretch()
        top_layout.addWidget(QLabel("Чемпионат:"))
        top_layout.addWidget(self.combo_champ)
        top_layout.addWidget(QLabel("Сезон:"))
        top_layout.addWidget(self.combo_season)

        tables_row_layout = QHBoxLayout()
        tables_row_layout.setSpacing(15)

        self.table_goals = self.create_ranking_table("БОМБАРДИРЫ")
        self.table_assists = self.create_ranking_table("АССИСТЕНТЫ")
        self.table_cards = self.create_ranking_table("НАРУШИТЕЛИ")

        tables_row_layout.addLayout(self.create_table_vbox("Лучшие бомбардиры", self.table_goals))
        tables_row_layout.addLayout(self.create_table_vbox("Лучшие ассистенты", self.table_assists))
        tables_row_layout.addLayout(self.create_table_vbox("Желтые карточки", self.table_cards))

        layout.addLayout(top_layout)
        layout.addLayout(tables_row_layout)

    def create_ranking_table(self, score_column_name):
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["ИГРОК", "КЛУБ", score_column_name])

        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setIconSize(QSize(30, 30))

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        return table

    def create_table_vbox(self, title, table):
        vbox = QVBoxLayout()
        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #555; margin-bottom: 5px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(lbl)
        vbox.addWidget(table)
        return vbox

    def load_championships(self):
        self.combo_champ.blockSignals(True)
        self.combo_champ.clear()
        self.combo_champ.addItem("Все чемпионаты", None)
        for c in data_manager.get_all("championships"):
            self.combo_champ.addItem(c['name'], c['championship_id'])
        self.combo_champ.blockSignals(False)
        self.load_seasons()

    def load_seasons(self):
        self.combo_season.blockSignals(True)
        self.combo_season.clear()
        self.combo_season.addItem("Все сезоны", None)
        champ_id = self.combo_champ.currentData()
        if champ_id:
            for s in data_manager.get_seasons(champ_id):
                self.combo_season.addItem(s['display_name'], s['season_id'])
        self.combo_season.blockSignals(False)
        self.refresh_all_tables()

    def refresh_all_tables(self):
        champ_id = self.combo_champ.currentData()
        season_id = self.combo_season.currentData()

        goals_data = data_manager.get_player_rankings(champ_id, season_id, 'Гол', False)
        assists_data = data_manager.get_player_rankings(champ_id, season_id, 'Гол', True)
        cards_data = data_manager.get_player_rankings(champ_id, season_id, 'ЖК', False)

        self.populate_single_table(self.table_goals, goals_data)
        self.populate_single_table(self.table_assists, assists_data)
        self.populate_single_table(self.table_cards, cards_data)

    def populate_single_table(self, table, data):
        table.setRowCount(0)
        for p in data:
            row = table.rowCount()
            table.insertRow(row)

            item_player = QTableWidgetItem(p['full_name'])
            photo = p.get('photo_path')
            if photo and os.path.exists(f"assets/players/{photo}"):
                item_player.setIcon(QIcon(f"assets/players/{photo}"))
            table.setItem(row, 0, item_player)

            table.setItem(row, 1, QTableWidgetItem(p.get('team_name') or "-"))

            item_total = QTableWidgetItem(str(p['total']))
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 2, item_total)