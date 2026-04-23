from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QScrollArea, QComboBox, QPushButton)
from PyQt6.QtCore import Qt
import locale
from controllers.data_manager import data_manager
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


class MatchesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_filters()
        self.refresh_matches()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        f_layout = QHBoxLayout()
        self.championships_box = QComboBox()
        self.season_box = QComboBox()
        self.round_box = QComboBox()
        self.team_box = QComboBox()
        reset_btn = QPushButton("СБРОСИТЬ ФИЛЬТРЫ")
        reset_btn.setFlat(True)
        reset_btn.setStyleSheet("color: #0000FF; font-weight: bold; font-size: 11px;")
        for label, box in [("ЧЕМПИОНАТ", self.championships_box), ("СЕЗОН", self.season_box), ("ТУР", self.round_box), ("КЛУБЫ", self.team_box)]:
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #888; font-weight: bold; font-size: 10px;")
            f_layout.addWidget(lbl)
            f_layout.addWidget(box)
            f_layout.addSpacing(15)

        f_layout.addStretch()
        f_layout.addWidget(reset_btn)
        main_layout.addLayout(f_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: #fdfdfd; }")

        self.container = QWidget()
        self.container.setStyleSheet("background: white;")
        self.m_layout = QVBoxLayout(self.container)
        self.m_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.m_layout.setSpacing(0)

        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)

        self.championships_box.currentIndexChanged.connect(self.refresh_matches)
        self.season_box.currentIndexChanged.connect(self.refresh_matches)
        self.round_box.currentIndexChanged.connect(self.refresh_matches)
        self.team_box.currentIndexChanged.connect(self.refresh_matches)
        reset_btn.clicked.connect(self.reset_filters)

    def load_filters(self):
        championships = data_manager.get_all("championships")
        for s in championships:
            self.championships_box.addItem(s.get('name'), userData=s.get('championship_id'))

        champ_id = self.championships_box.currentData()
        seasons = data_manager.get_all("seasons")
        filtered_seasons = [s for s in seasons if s['championship_id'] == champ_id]
        for s in filtered_seasons:
            self.season_box.addItem(s.get('season_label', str(s['start_date'])), s['season_id'])

        self.team_box.addItem("Все клубы", None)
        teams = data_manager.get_all("teams")
        for t in sorted(teams, key=lambda x: x['name']):
            self.team_box.addItem(t['name'], t['team_id'])

        self.round_box.addItem("Все туры")
        for r in range(1, 31):
            self.round_box.addItem(f"Тур {r}")

    def reset_filters(self):
        self.season_box.setCurrentIndex(0)
        self.round_box.setCurrentIndex(0)
        self.team_box.setCurrentIndex(0)
        self.refresh_matches()

    def refresh_matches(self):
        season_id = self.season_box.currentData()
        round_val = self.round_box.currentText()
        team_id = self.team_box.currentData()

        if not season_id: return

        while self.m_layout.count():
            child = self.m_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        matches = data_manager.get_filtered_matches(season_id, round_val, team_id)

        last_date = None
        for m in matches:
            m_date = m['match_date']
            header_str = m_date.strftime("%A, %d %B %Y").capitalize()

            if header_str != last_date:
                lbl = QLabel(header_str)
                lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #000080; padding: 20px 0 10px 10px;")
                self.m_layout.addWidget(lbl)
                last_date = header_str

            self.m_layout.addWidget(MatchCardWidget(m))

        self.m_layout.addStretch(1)


class MatchCardWidget(QFrame):
    def __init__(self, match_data):
        super().__init__()
        self.match_data = match_data
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            MatchCardWidget {
                border-bottom: 1px solid #e0e0e0;
                background-color: white;
            }
            QLabel { border: none; }
        """)
        self.setFixedHeight(60)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        info_layout = QVBoxLayout()
        round_lbl = QLabel(f"Тур {self.match_data.get('round', '')}")
        round_lbl.setStyleSheet("color: #757575; font-size: 11px;")
        round_lbl.setFixedWidth(120)

        time_lbl = QLabel(self.match_data.get('time', ''))
        time_lbl.setStyleSheet("color: #757575; font-size: 11px;")
        time_lbl.setFixedWidth(120)

        info_layout.addWidget(round_lbl)
        info_layout.addWidget(time_lbl)

        status_lbl = QLabel(self.match_data.get('status', 'Завершен'))
        status_lbl.setStyleSheet("color: #757575; font-size: 12px;")
        status_lbl.setFixedWidth(80)

        home_lbl = QLabel(self.match_data.get('home_team', ''))
        home_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        home_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")
        home_lbl.setFixedWidth(160)

        score_lbl = QLabel(f"{self.match_data.get('home_score', 0)} - {self.match_data.get('away_score', 0)}")
        score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_lbl.setFixedSize(50, 30)
        score_lbl.setStyleSheet("""
            background-color: #f5f5f5;
            border-radius: 5px;
            font-weight: bold;
            font-size: 14px;
        """)

        away_lbl = QLabel(self.match_data.get('away_team', ''))
        away_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        away_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")
        away_lbl.setFixedWidth(160)

        loc_layout = QVBoxLayout()
        city_lbl = QLabel(self.match_data.get('city', ''))
        city_lbl.setStyleSheet("color: #757575; font-size: 11px;")
        city_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        city_lbl.setFixedWidth(120)

        stadium_lbl = QLabel(self.match_data.get('stadium', ''))
        stadium_lbl.setStyleSheet("color: #757575; font-size: 11px;")
        stadium_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        stadium_lbl.setFixedWidth(120)

        loc_layout.addWidget(city_lbl)
        loc_layout.addWidget(stadium_lbl)

        layout.addLayout(info_layout)
        layout.addWidget(status_lbl)
        layout.addStretch(1)
        layout.addWidget(home_lbl)
        layout.addWidget(score_lbl)
        layout.addWidget(away_lbl)
        layout.addStretch(1)

        layout.addLayout(loc_layout)


