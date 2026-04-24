from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QScrollArea, QComboBox, QPushButton, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from controllers.data_manager import data_manager
import os

class TeamsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_filters()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        f_layout = QHBoxLayout()
        self.championships_box = QComboBox()
        self.season_box = QComboBox()

        self.championships_box.setFixedWidth(200)
        self.season_box.setFixedWidth(150)

        reset_btn = QPushButton("СБРОСИТЬ ФИЛЬТРЫ")
        reset_btn.setFlat(True)
        reset_btn.setStyleSheet("color: #0000FF; font-weight: bold; font-size: 11px;")

        for label, box in [("ЧЕМПИОНАТ", self.championships_box), ("СЕЗОН", self.season_box)]:
            v_layout = QVBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #888; font-weight: bold; font-size: 10px;")
            v_layout.addWidget(lbl)
            v_layout.addWidget(box)
            f_layout.addLayout(v_layout)
            f_layout.addSpacing(10)

        f_layout.addStretch()
        f_layout.addWidget(reset_btn)
        main_layout.addLayout(f_layout)

        self.title_lbl = QLabel("")
        self.title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #000040;")
        main_layout.addWidget(self.title_lbl)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: #fdfdfd; }")

        self.container = QWidget()
        self.container.setStyleSheet("background: white;")

        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.grid_layout.setSpacing(15)

        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)

        # --- СИГНАЛЫ ---
        self.championships_box.currentIndexChanged.connect(self.on_championship_changed)
        self.season_box.currentIndexChanged.connect(self.refresh_teams)
        reset_btn.clicked.connect(self.reset_filters)

    def load_filters(self):
        self.championships_box.blockSignals(True)
        self.championships_box.clear()

        championships = data_manager.get_all("championships")
        for c in championships:
            self.championships_box.addItem(c.get('name'), c.get('championship_id'))

        self.championships_box.blockSignals(False)
        self.on_championship_changed()

    def on_championship_changed(self):
        champ_id = self.championships_box.currentData()
        champ_name = self.championships_box.currentText()

        self.title_lbl.setText(champ_name)

        if champ_id is None: return

        self.season_box.blockSignals(True)
        self.season_box.clear()

        seasons = data_manager.get_seasons(champ_id)
        for s in seasons:
            label = f"{str(s['start_date'])[:4]} - {str(s['end_date'])[:4]}"
            self.season_box.addItem(label, s['season_id'])

        self.season_box.blockSignals(False)
        self.refresh_teams()

    def reset_filters(self):
        self.championships_box.setCurrentIndex(0)

    def refresh_teams(self):
        season_id = self.season_box.currentData()
        if season_id is None: return

        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        teams = data_manager.get_teams(season_id)

        max_columns = 4
        row = 0
        col = 0

        for t in teams:
            self.grid_layout.addWidget(TeamCardWidget(t), row, col)
            col += 1
            if col >= max_columns:
                col = 0
                row += 1


class TeamCardWidget(QFrame):
    def __init__(self, team_data):
        super().__init__()
        self.team_data = team_data
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(260, 110)
        self.setStyleSheet("""
            TeamCardWidget {
                background-color: white;
                border: 1px solid #eaeaea;
                border-radius: 8px;
            }
            TeamCardWidget:hover {
                border: 1px solid #b0b0b0;
                background-color: #fafafa;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        top_layout = QHBoxLayout()

        self.logo_lbl = QLabel()
        self.logo_lbl.setFixedSize(50, 50)
        self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_path = self.team_data.get('logo_path')
        full_path = os.path.join("assets", "teams", str(logo_path)) if logo_path else ""
        if logo_path and os.path.exists(full_path):
            pixmap = QPixmap(full_path)
            scaled_pixmap = pixmap.scaled(
                self.logo_lbl.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.logo_lbl.setPixmap(scaled_pixmap)
        else:
            self.logo_lbl.setStyleSheet("""
                background-color: #f0f0f0; 
                border-radius: 25px; 
                color: #ccc; 
                font-size: 8px;
            """)
            self.logo_lbl.setText("")

        name_lbl = QLabel(self.team_data.get('name', 'Команда'))
        name_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #000040;")
        name_lbl.setWordWrap(True)

        top_layout.addWidget(self.logo_lbl)
        top_layout.addSpacing(15)
        top_layout.addWidget(name_lbl)
        top_layout.addStretch()

        city_layout = QVBoxLayout()
        gorod_hint_lbl = QLabel("ГОРОД")
        gorod_hint_lbl.setStyleSheet("font-size: 9px; color: #999; font-weight: bold;")
        city_name_lbl = QLabel(self.team_data.get('city', 'Неизвестно'))
        city_name_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #222;")

        city_layout.addWidget(gorod_hint_lbl)
        city_layout.addWidget(city_name_lbl)

        main_layout.addLayout(top_layout)
        main_layout.addStretch()
        main_layout.addLayout(city_layout)