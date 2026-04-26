from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QScrollArea, QComboBox, QPushButton, QGridLayout)
from PyQt6.QtCore import Qt
import locale
from controllers.data_manager import data_manager
locale.setlocale(locale.LC_TIME, 'russian')


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
        self.championships_box.setFixedWidth(150)
        self.season_box = QComboBox()
        self.season_box.setFixedWidth(150)
        self.round_box = QComboBox()
        self.round_box.setFixedWidth(150)
        self.team_box = QComboBox()
        self.team_box.setFixedWidth(150)
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

        self.championships_box.currentIndexChanged.connect(self.on_championship_changed)
        self.season_box.currentIndexChanged.connect(self.on_season_changed)
        self.round_box.currentIndexChanged.connect(self.refresh_matches)
        self.team_box.currentIndexChanged.connect(self.refresh_matches)

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

        for box in [self.season_box, self.team_box, self.round_box]:
            box.clear()
        self.season_box.blockSignals(True)
        self.team_box.blockSignals(True)
        self.season_box.clear()
        seasons = data_manager.get_seasons(champ_id)
        for s in seasons:
            label = f"{str(s['start_date'])[:4]} - {str(s['end_date'])[:4]}"
            self.season_box.addItem(label, s['season_id'])


        self.season_box.blockSignals(False)
        self.team_box.blockSignals(False)
        self.on_season_changed()

    def on_season_changed(self):
        season_id = self.season_box.currentData()
        if not season_id: return
        self.round_box.blockSignals(True)
        self.team_box.blockSignals(True)
        self.round_box.clear()
        self.team_box.clear()
        self.round_box.addItem("Все туры", None)
        existing_rounds = data_manager.get_tours(season_id)
        for r in existing_rounds:
            self.round_box.addItem(f"Тур {r}", r)

        self.team_box.addItem("Все клубы", None)
        teams = data_manager.get_teams(season_id)
        for t in sorted(teams, key=lambda x: x['name']):
            self.team_box.addItem(t['name'], t['team_id'])
        self.team_box.blockSignals(False)
        self.round_box.blockSignals(False)
        self.refresh_matches()

    def reset_filters(self):
        self.season_box.setCurrentIndex(0)
        self.round_box.setCurrentIndex(0)
        self.team_box.setCurrentIndex(0)
        self.refresh_matches()

    def refresh_matches(self):
        while self.m_layout.count():
            item = self.m_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        season_id = self.season_box.currentData()
        if season_id is None:

            return
        round_val = self.round_box.currentData()
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
        self.stats_loaded = False
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            MatchCardWidget {
                border-bottom: 1px solid #e0e0e0;
                background-color: white;
            }
            QLabel { border: none; }
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.top_container = QWidget()
        self.top_container.setMinimumHeight(60)
        top_layout = QHBoxLayout(self.top_container)
        top_layout.setContentsMargins(10, 5, 10, 5)

        info_layout = QVBoxLayout()
        round_lbl = QLabel(f"Тур {self.match_data.get('tour', '')}")
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
        score_lbl.setStyleSheet("background-color: #f5f5f5; border-radius: 5px; font-weight: bold; font-size: 14px;")

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

        self.btn_stats = QPushButton("▼ Статистика")
        self.btn_stats.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stats.setFlat(True)
        self.btn_stats.setStyleSheet("color: #1976D2; font-weight: bold; font-size: 11px; border: none;")
        self.btn_stats.clicked.connect(self.toggle_stats)

        # Собираем верхний слой
        top_layout.addLayout(info_layout)
        top_layout.addWidget(status_lbl)
        top_layout.addStretch(1)
        top_layout.addWidget(home_lbl)
        top_layout.addWidget(score_lbl)
        top_layout.addWidget(away_lbl)
        top_layout.addStretch(1)
        top_layout.addLayout(loc_layout)
        top_layout.addWidget(self.btn_stats)

        self.main_layout.addWidget(self.top_container)

        self.stats_container = QFrame()
        self.stats_container.setStyleSheet("background-color: #fafafa; border-top: 1px solid #eeeeee;")
        self.stats_layout = QVBoxLayout(self.stats_container)
        self.stats_layout.setContentsMargins(40, 15, 40, 15)

        self.stats_container.hide()
        self.main_layout.addWidget(self.stats_container)

    def toggle_stats(self):
        if self.stats_container.isVisible():
            self.stats_container.hide()
            self.btn_stats.setText("▼ Статистика")
        else:
            if not self.stats_loaded:
                self.build_stats_ui()
            print("1")
            self.stats_container.show()
            self.btn_stats.setText("▲ Статистика")

    def build_stats_ui(self):
        match_id = self.match_data.get('match_id')
        raw_stats = data_manager.get_match_stats(match_id)
        if not raw_stats or len(raw_stats) < 2:
            no_data_lbl = QLabel("Статистика для данного матча пока недоступна")
            no_data_lbl.setStyleSheet("color: #757575; font-style: italic;")
            no_data_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.stats_layout.addWidget(no_data_lbl)
            self.stats_loaded = True
            return
        home_team_name = self.match_data.get('home_team')
        away_team_name = self.match_data.get('away_team')

        if raw_stats[0]['team_name'] == home_team_name:
            stat_home = raw_stats[0]
            stat_away = raw_stats[1]
        else:
            stat_home = raw_stats[1]
            stat_away = raw_stats[0]

        grid = QGridLayout()
        grid.setVerticalSpacing(10)

        h_name = QLabel(home_team_name)
        h_name.setStyleSheet("font-weight: bold; font-size: 12px; color: #333;")
        h_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        a_name = QLabel(away_team_name)
        a_name.setStyleSheet("font-weight: bold; font-size: 12px; color: #333;")
        a_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        grid.addWidget(h_name, 0, 0)
        grid.addWidget(a_name, 0, 2)

        stat_rows = [
            ("Владение мячом (%)", 'possession'),
            ("Удары", 'shots'),
            ("Удары в створ", 'shots_on_target'),
            ("Угловые", 'corners'),
            ("Фолы", 'fouls'),
            ("Офсайды", 'offsides')
        ]

        row_idx = 1
        for label_text, db_key in stat_rows:
            val_h = QLabel(str(stat_home.get(db_key, 0)))
            val_h.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val_h.setStyleSheet("font-size: 14px; font-weight: bold;")

            lbl = QLabel(label_text)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #757575; font-size: 12px;")

            val_a = QLabel(str(stat_away.get(db_key, 0)))
            val_a.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val_a.setStyleSheet("font-size: 14px; font-weight: bold;")

            grid.addWidget(val_h, row_idx, 0)
            grid.addWidget(lbl, row_idx, 1)
            grid.addWidget(val_a, row_idx, 2)

            grid.setColumnStretch(0, 1)
            grid.setColumnStretch(1, 2)
            grid.setColumnStretch(2, 1)

            row_idx += 1

        self.stats_layout.addLayout(grid)
        self.stats_loaded = True

