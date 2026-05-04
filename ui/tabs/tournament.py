from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                             QHeaderView, QHBoxLayout, QComboBox, QTableWidgetItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import os
from controllers.data_manager import data_manager


class TournamentTable(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_championships()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        title = QLabel("Турнирная таблица")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00bcd4;")

        self.champ_box = QComboBox()
        self.champ_box.setFixedWidth(200)
        self.champ_box.currentIndexChanged.connect(self.load_seasons)

        self.season_box = QComboBox()
        self.season_box.setFixedWidth(150)
        self.season_box.currentIndexChanged.connect(self.refresh_table)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Чемпионат:"))
        header_layout.addWidget(self.champ_box)
        header_layout.addWidget(QLabel("Сезон:"))
        header_layout.addWidget(self.season_box)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "№", "Команда", "И", "В", "Н", "П", "Мячи", "Очки", "Форма"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("gridline-color: #e0e0e0; font-size: 14px;")

        layout.addWidget(self.table)

    def load_championships(self):
        self.champ_box.clear()
        champs = data_manager.get_all("championships")
        for c in champs:
            self.champ_box.addItem(c['name'], userData=c['championship_id'])

    def load_seasons(self):
        self.season_box.clear()
        champ_id = self.champ_box.currentData()
        seasons = data_manager.get_seasons(champ_id)
        for s in seasons:
            self.season_box.addItem(s['display_name'], s['season_id'])
        self.refresh_table()

    def refresh_table(self):
        season_id = self.season_box.currentData()
        if not season_id:
            self.table.setRowCount(0)
            return
        data = data_manager.get_tournament_data(season_id)
        self.table.setRowCount(len(data))

        for i, row in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))

            team_item = QTableWidgetItem(row['name'])
            if row.get('full_logo_path'):
                team_item.setIcon(QIcon(row['full_logo_path']))

            self.table.setItem(i, 1, team_item)
            self.table.setItem(i, 2, QTableWidgetItem(str(row['played'])))
            self.table.setItem(i, 3, QTableWidgetItem(str(row['win'])))
            self.table.setItem(i, 4, QTableWidgetItem(str(row['draw'])))
            self.table.setItem(i, 5, QTableWidgetItem(str(row['loss'])))

            self.table.setItem(i, 6, QTableWidgetItem(row['goals_stat']))
            pts_item = QTableWidgetItem(str(row['pts']))
            pts_item.setData(Qt.ItemDataRole.TextAlignmentRole, Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 7, pts_item)
            self.table.setCellWidget(i, 8, self.create_form_widget(row['form_list']))

    def create_form_widget(self, form_data):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        for res in form_data:
            label = QLabel(res)
            label.setFixedSize(20, 20)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            color = "#4CAF50" if res == 'В' else "#F44336" if res == 'П' else "#FFC107"
            label.setStyleSheet(
                f"background-color: {color}; color: white; border-radius: 10px; font-weight: bold;"
            )
            layout.addWidget(label)

        return container