import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                             QLineEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLabel)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
from controllers.data_manager import data_manager


class PlayersTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_nationalities()
        self.load_championships()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        top_layout = QHBoxLayout()
        title_lbl = QLabel("Игроки")
        title_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #00bcd4;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по ФИО...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.filter_table)

        top_layout.addWidget(title_lbl)
        top_layout.addStretch()
        top_layout.addWidget(self.search_input)

        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(10)

        self.combo_champ = QComboBox()
        self.combo_season = QComboBox()
        self.combo_club = QComboBox()

        self.combo_position = QComboBox()
        self.combo_position.addItems(["Все амплуа", "Вратарь", "Защитник", "Полузащитник", "Нападающий"])

        self.combo_nationality = QComboBox()

        self.combo_champ.currentIndexChanged.connect(self.load_seasons)
        self.combo_season.currentIndexChanged.connect(self.load_teams)
        self.combo_club.currentIndexChanged.connect(self.filter_table)
        self.combo_position.currentIndexChanged.connect(self.filter_table)
        self.combo_nationality.currentIndexChanged.connect(self.filter_table)

        filters_layout.addWidget(QLabel("Чемпионат:"))
        filters_layout.addWidget(self.combo_champ)
        filters_layout.addWidget(QLabel("Сезон:"))
        filters_layout.addWidget(self.combo_season)
        filters_layout.addWidget(QLabel("Клуб:"))
        filters_layout.addWidget(self.combo_club)
        filters_layout.addWidget(QLabel("Амплуа:"))
        filters_layout.addWidget(self.combo_position)
        filters_layout.addWidget(QLabel("Страна:"))
        filters_layout.addWidget(self.combo_nationality)
        filters_layout.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ИГРОК", "КЛУБ", "АМПЛУА", "ДАТА РОЖДЕНИЯ", "ГРАЖДАНСТВО"])

        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.setIconSize(QSize(30, 30))
        self.table.setStyleSheet("gridline-color: #e0e0e0; font-size: 14px;")

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        layout.addLayout(top_layout)
        layout.addLayout(filters_layout)
        layout.addWidget(self.table)

    def load_nationalities(self):
        """Загружаем уникальные страны из БД"""
        self.combo_nationality.blockSignals(True)
        self.combo_nationality.clear()
        self.combo_nationality.addItem("Все страны", None)

        nationalities = data_manager.get_national()
        for n in nationalities:
            if n:
                self.combo_nationality.addItem(n, n)

        self.combo_nationality.blockSignals(False)

    def load_championships(self):
        """Загружаем чемпионаты (как в TournamentTable)"""
        self.combo_champ.blockSignals(True)
        self.combo_champ.clear()
        self.combo_champ.addItem("Все чемпионаты", None)

        champs = data_manager.get_all("championships")  # Берем из твоей БД
        for c in champs:
            self.combo_champ.addItem(c['name'], c['championship_id'])

        self.combo_champ.blockSignals(False)
        self.load_seasons()

    def load_seasons(self):
        """Загружаем сезоны в зависимости от выбранного чемпионата"""
        self.combo_season.blockSignals(True)
        self.combo_season.clear()
        self.combo_season.addItem("Все сезоны", None)

        champ_id = self.combo_champ.currentData()
        if champ_id:
            seasons = data_manager.get_seasons(champ_id)
            for s in seasons:
                label = f"{str(s['start_date'])[:4]} - {str(s['end_date'])[:4]}"
                self.combo_season.addItem(label, s['season_id'])

        self.combo_season.blockSignals(False)
        self.load_teams()

    def load_teams(self):
        self.combo_club.blockSignals(True)
        self.combo_club.clear()
        self.combo_club.addItem("Все клубы", None)

        season_id = self.combo_season.currentData()
        if season_id:
            teams = data_manager.get_teams(season_id)
            for t in sorted(teams, key=lambda x: x['name']):
                self.combo_club.addItem(t['name'], t['team_id'])

        self.combo_club.blockSignals(False)
        self.filter_table()


    def filter_table(self):
        championship_id = self.combo_champ.currentData()
        season_id = self.combo_season.currentData()
        club_id = self.combo_club.currentData()
        position = self.combo_position.currentText()
        nationality = self.combo_nationality.currentData()
        search_text = self.search_input.text().strip()

        if not search_text: search_text = None

        players_data = data_manager.get_filtered_players(
            championship_id=championship_id,
            season_id=season_id,
            club_id=club_id,
            position=position,
            nationality=nationality,
            search_text=search_text
        )

        self.populate_table(players_data)

    def populate_table(self, players_data):
        self.table.setRowCount(0)

        for p in players_data:
            row = self.table.rowCount()
            self.table.insertRow(row)

            item_player = QTableWidgetItem(p.get('full_name', 'Неизвестно'))
            photo = p.get('photo')  # Или photo_path, в зависимости от твоей таблицы
            if photo and os.path.exists(f"assets/players/{photo}"):
                item_player.setIcon(QIcon(f"assets/players/{photo}"))
            self.table.setItem(row, 0, item_player)

            team_name = p.get('team_name') or "Свободный агент"
            item_club = QTableWidgetItem(team_name)
            logo = p.get('logo_path')
            if logo and os.path.exists(f"assets/teams/{logo}"):
                item_club.setIcon(QIcon(f"assets/teams/{logo}"))
            self.table.setItem(row, 1, item_club)

            self.table.setItem(row, 2, QTableWidgetItem(p.get('position', '-')))

            birth_date = p.get('birth_date')
            item_date = QTableWidgetItem(birth_date.strftime("%d.%m.%Y") if birth_date else "-")
            item_date.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, item_date)

            self.table.setItem(row, 4, QTableWidgetItem(p.get('nationality', '-')))