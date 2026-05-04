from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import locale
import os
from controllers.data_manager import data_manager
from controllers.session import session
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
        reset_btn = QPushButton("Обновить")
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

        reset_btn.clicked.connect(self.update_filters)

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
            self.season_box.addItem(s['display_name'], s['season_id'])


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

    def update_filters(self):
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
                    MatchCardWidget { border-bottom: 1px solid #e0e0e0; background-color: white; }
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

        self.home_logo = QLabel()
        self.home_logo.setFixedSize(30, 30)
        self.home_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.away_logo = QLabel()
        self.away_logo.setFixedSize(30, 30)
        self.away_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.set_logo(self.home_logo, self.match_data.get('home_logo'))
        self.set_logo(self.away_logo, self.match_data.get('away_logo'))

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

        buttons_layout = QHBoxLayout()
        if session.current_role in ["admin", "manager"]:
            self.btn_edit = QPushButton("Изменить")
            self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_edit.setFlat(True)
            self.btn_edit.setStyleSheet("color: #D32F2F; font-weight: bold; font-size: 11px;")
            self.btn_edit.clicked.connect(self.open_edit_dialog)
            buttons_layout.addWidget(self.btn_edit)

        self.btn_stats = QPushButton("▼ Статистика")
        self.btn_stats.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stats.setFlat(True)
        self.btn_stats.setStyleSheet("color: #1976D2; font-weight: bold; font-size: 11px;")
        self.btn_stats.clicked.connect(self.toggle_stats)
        buttons_layout.addWidget(self.btn_stats)

        top_layout.addLayout(info_layout)
        top_layout.addWidget(status_lbl)
        top_layout.addStretch(1)
        top_layout.addWidget(home_lbl)
        top_layout.addWidget(self.home_logo)
        top_layout.addWidget(score_lbl)
        top_layout.addWidget(self.away_logo)
        top_layout.addWidget(away_lbl)
        top_layout.addStretch(1)
        top_layout.addLayout(loc_layout)
        top_layout.addLayout(buttons_layout)

        self.main_layout.addWidget(self.top_container)

        self.stats_container = QFrame()
        self.stats_container.setStyleSheet("background-color: #fafafa; border-top: 1px solid #eeeeee;")
        self.stats_layout = QVBoxLayout(self.stats_container)
        self.stats_container.hide()
        self.main_layout.addWidget(self.stats_container)

    def open_edit_dialog(self):
        dialog = MatchEditDialog(self.match_data, self)
        if dialog.exec():
            parent_tab = self.window().findChild(MatchesTab)
            if parent_tab:
                parent_tab.refresh_matches()



    def set_logo(self, label, logo_path):
        full_path = os.path.join("assets", "teams", str(logo_path)) if logo_path else ""

        if logo_path and os.path.exists(full_path):
            pixmap = QPixmap(full_path)
            scaled_pixmap = pixmap.scaled(
                label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            label.setPixmap(scaled_pixmap)
        else:
            label.setStyleSheet("""
                background-color: #f0f0f0; 
                border-radius: 15px;
            """)

    def toggle_stats(self):
        if self.stats_container.isVisible():
            self.stats_container.hide()
            self.btn_stats.setText("▼ Статистика")
        else:
            if not self.stats_loaded:
                self.build_stats_ui()
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

class MatchEditDialog(QDialog):
    def __init__(self, match_data, parent=None):
        super().__init__(parent)
        self.match_data = match_data

        self.setWindowTitle(
            f"{match_data.get('home_team')} - {match_data.get('away_team')}"
        )
        self.resize(500, 450)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        tab_main = QWidget()
        main_layout = QVBoxLayout(tab_main)

        main_layout.addStretch()

        score_group = QGroupBox("Текущий счет")
        score_group.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_layout = QHBoxLayout(score_group)
        score_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_layout.setSpacing(15)

        home_lbl = QLabel(self.match_data.get('home_team'))
        home_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.spin_home = QSpinBox()
        self.spin_home.setFixedSize(60, 40)
        self.spin_home.setStyleSheet("font-size: 18px;")
        self.spin_home.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_home.setValue(self.match_data.get('home_score', 0))

        dash_lbl = QLabel("-")
        dash_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.spin_away = QSpinBox()
        self.spin_away.setFixedSize(60, 40)
        self.spin_away.setStyleSheet("font-size: 18px;")
        self.spin_away.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_away.setValue(self.match_data.get('away_score', 0))

        away_lbl = QLabel(self.match_data.get('away_team'))
        away_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")

        score_layout.addWidget(home_lbl)
        score_layout.addWidget(self.spin_home)
        score_layout.addWidget(dash_lbl)
        score_layout.addWidget(self.spin_away)
        score_layout.addWidget(away_lbl)

        status_layout = QHBoxLayout()
        status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        status_lbl = QLabel("Статус матча:")
        status_lbl.setStyleSheet("font-size: 14px;")

        self.combo_status = QComboBox()
        self.combo_status.setFixedWidth(150)
        self.combo_status.addItems(["Не начался", "Сыгран", "Перенесен", "Отменен"])
        self.combo_status.setCurrentText(self.match_data.get('status', 'Сыгран'))

        status_layout.addWidget(status_lbl)
        status_layout.addWidget(self.combo_status)

        main_layout.addWidget(score_group)
        main_layout.addSpacing(20)
        main_layout.addLayout(status_layout)

        main_layout.addStretch()

        self.tabs.addTab(tab_main, "Результат")

        tab_stats = QWidget()
        stats_main_layout = QVBoxLayout(tab_stats)

        stats_group = QGroupBox("Командная статистика")
        stats_layout = QGridLayout(stats_group)
        stats_layout.setHorizontalSpacing(30)
        stats_layout.setVerticalSpacing(10)

        def spin():
            s = QSpinBox()
            s.setRange(0, 200)
            s.setFixedWidth(70)
            s.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return s

        self.home_poss, self.away_poss = spin(), spin()
        self.home_shots, self.away_shots = spin(), spin()
        self.home_shots_on, self.away_shots_on = spin(), spin()
        self.home_corners, self.away_corners = spin(), spin()
        self.home_fouls, self.away_fouls = spin(), spin()
        self.home_offsides, self.away_offsides = spin(), spin()

        rows = [
            ("Владение (%)", self.home_poss, self.away_poss),
            ("Удары", self.home_shots, self.away_shots),
            ("В створ", self.home_shots_on, self.away_shots_on),
            ("Угловые", self.home_corners, self.away_corners),
            ("Фолы", self.home_fouls, self.away_fouls),
            ("Офсайды", self.home_offsides, self.away_offsides),
        ]

        lbl_home = QLabel(self.match_data.get('home_team'))
        lbl_home.setStyleSheet("font-weight: bold;")
        lbl_home.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_param = QLabel("ПОКАЗАТЕЛЬ")
        lbl_param.setStyleSheet("font-weight: bold; color: gray;")
        lbl_param.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_away = QLabel(self.match_data.get('away_team'))
        lbl_away.setStyleSheet("font-weight: bold;")
        lbl_away.setAlignment(Qt.AlignmentFlag.AlignCenter)

        stats_layout.addWidget(lbl_home, 0, 0)
        stats_layout.addWidget(lbl_param, 0, 1)
        stats_layout.addWidget(lbl_away, 0, 2)

        for i, (label, h, a) in enumerate(rows, 1):
            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stats_layout.addWidget(h, i, 0, Qt.AlignmentFlag.AlignCenter)
            stats_layout.addWidget(lbl, i, 1)
            stats_layout.addWidget(a, i, 2, Qt.AlignmentFlag.AlignCenter)

        stats_main_layout.addStretch()
        stats_main_layout.addWidget(stats_group)
        stats_main_layout.addStretch()

        self.tabs.addTab(tab_stats, "Статистика")
        tab_events = QWidget()
        events_layout = QVBoxLayout(tab_events)

        self.events_list = QListWidget()
        events_layout.addWidget(QLabel("Протокол матча:"))
        events_layout.addWidget(self.events_list)

        btn_add_event = QPushButton("+ Добавить событие")
        btn_add_event.clicked.connect(self.add_event)
        events_layout.addWidget(btn_add_event)

        self.tabs.addTab(tab_events, "События")

        layout.addWidget(self.tabs)

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Сохранить")
        btn_save.setFixedSize(120, 35)
        btn_save.setStyleSheet("background-color: #1976D2; color: white; font-weight: bold;")
        btn_save.clicked.connect(self.save_changes)

        btn_cancel = QPushButton("Отмена")
        btn_cancel.setFixedSize(120, 35)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

        self.load_stats()
        self.load_events()

    def load_stats(self):
        stats = data_manager.get_match_stats(self.match_data["match_id"])

        if not stats or len(stats) < 2:
            return

        home_team = self.match_data["home_team"]

        if stats[0]["team_name"] == home_team:
            h, a = stats[0], stats[1]
        else:
            h, a = stats[1], stats[0]

        self.home_poss.setValue(h["possession"])
        self.away_poss.setValue(a["possession"])

        self.home_shots.setValue(h["shots"])
        self.away_shots.setValue(a["shots"])

        self.home_shots_on.setValue(h["shots_on_target"])
        self.away_shots_on.setValue(a["shots_on_target"])

        self.home_corners.setValue(h["corners"])
        self.away_corners.setValue(a["corners"])

        self.home_fouls.setValue(h["fouls"])
        self.away_fouls.setValue(a["fouls"])

        self.home_offsides.setValue(h["offsides"])
        self.away_offsides.setValue(a["offsides"])

    def load_events(self):
        self.events_list.clear()
        events = data_manager.get_events(self.match_data["match_id"])

        for e in events:
            text = f"{e['minute']}' {e['player_name']} ({e['team_name']}) - {e['event_type']}"
            self.events_list.addItem(text)

    def add_event(self):
        dialog = AddEventDialog(self.match_data, self)

        if dialog.exec():
            data = dialog.get_data()
            success = data_manager.add_match_event(data)

            if success:
                self.load_events()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить событие")

    def save_changes(self):
        match_id = self.match_data["match_id"]
        home_team = self.match_data["home_team"]

        match_update = {
            "home_score": self.spin_home.value(),
            "away_score": self.spin_away.value(),
            "status": self.combo_status.currentText()
        }

        stats_home = {
            "match_id": match_id,
            "team_id": self.match_data["home_team_id"],
            "possession": self.home_poss.value(),
            "shots": self.home_shots.value(),
            "shots_on_target": self.home_shots_on.value(),
            "corners": self.home_corners.value(),
            "fouls": self.home_fouls.value(),
            "offsides": self.home_offsides.value(),
        }

        stats_away = {
            "match_id": match_id,
            "team_id": self.match_data["away_team_id"],
            "possession": self.away_poss.value(),
            "shots": self.away_shots.value(),
            "shots_on_target": self.away_shots_on.value(),
            "corners": self.away_corners.value(),
            "fouls": self.away_fouls.value(),
            "offsides": self.away_offsides.value(),
        }

        success, title, msg = data_manager.update_match_and_stats(
            match_id, home_team, match_update, stats_home, stats_away
        )

        if success:
            QMessageBox.information(self, title, msg)
            self.accept()
        else:
            QMessageBox.warning(self, title, msg)


class AddEventDialog(QDialog):
    def __init__(self, match_data, parent=None):
        super().__init__(parent)
        self.match_data = match_data
        self.setWindowTitle("Добавить событие")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.team_box = QComboBox()
        self.team_box.addItem(match_data["home_team"], match_data["home_team_id"])
        self.team_box.addItem(match_data["away_team"], match_data["away_team_id"])

        self.player_box = QComboBox()

        self.assist_box = QComboBox()
        self.assist_box.addItem("Нет", None)

        self.event_type = QComboBox()
        self.event_type.addItems(["Гол", "ЖК", "КК"])

        self.minute = QSpinBox()
        self.minute.setRange(1, 120)

        form_layout.addRow("Команда:", self.team_box)
        form_layout.addRow("Игрок:", self.player_box)
        form_layout.addRow("Ассист:", self.assist_box)
        form_layout.addRow("Тип:", self.event_type)
        form_layout.addRow("Минута:", self.minute)

        layout.addLayout(form_layout)

        btn = QPushButton("Добавить")
        btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px;")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

        self.team_box.currentIndexChanged.connect(self.load_players)
        self.load_players()

    def load_players(self):
        team_id = self.team_box.currentData()
        match_id = self.match_data["match_id"]

        players = data_manager.get_players_for_match_team(match_id, team_id)

        self.player_box.clear()
        self.assist_box.clear()
        self.assist_box.addItem("Нет", None)

        for p in players:
            self.player_box.addItem(p["full_name"], p["player_id"])
            self.assist_box.addItem(p["full_name"], p["player_id"])

    def get_data(self):
        return {
            "match_id": self.match_data["match_id"],
            "team_id": self.team_box.currentData(),
            "player_id": self.player_box.currentData(),
            "assist_player_id": self.assist_box.currentData(),
            "event_type": self.event_type.currentText(),
            "minute": self.minute.value()
        }