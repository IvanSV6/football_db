import datetime
import os
import shutil
from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QCheckBox,
                             QDateEdit, QComboBox, QMessageBox, QFileDialog, QWidget, QHBoxLayout)
from PyQt6.QtCore import QDate
from config import TABLE_CONFIG
from controllers.data_manager import data_manager


class UniversalDialog(QDialog):
    def __init__(self, table_name, current_data=None, parent=None):
        super().__init__(parent)
        self.config = TABLE_CONFIG[table_name]
        self.inputs = {}
        self.current_data = current_data

        title_prefix = "Редактирование" if current_data else "Добавление"
        self.setWindowTitle(f"{title_prefix}: {self.config['title']}")

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        for field in self.config["fields"]:
            if field["type"] == "hidden":
                continue

            col_name = field["column"]
            widget = self.create_widget(field)
            form.addRow(field["label"] + ":", widget)
            self.inputs[col_name] = widget

        season_box = self.inputs.get("season_id")
        has_teams = any(k in self.inputs for k in ["home_team_id", "away_team_id", "team_id"])

        if season_box and has_teams:
            season_box.currentIndexChanged.connect(self.update_teams_combos)

        if self.current_data:
            if "season_id" in self.inputs and "season_id" in self.current_data:
                self.set_widget_value(self.inputs["season_id"], "combo", self.current_data["season_id"])

            for field in self.config["fields"]:
                col_name = field["column"]
                if field["type"] == "hidden" or col_name == "season_id":
                    continue
                if col_name in self.current_data:
                    self.set_widget_value(self.inputs[col_name], field["type"], self.current_data[col_name])
        else:
            if has_teams:
                self.update_teams_combos()

        layout.addLayout(form)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

    def create_widget(self, field):
        f_type = field["type"]

        if f_type == "boolean":
            return QCheckBox()
        elif f_type == "date":
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            widget.setDate(QDate.currentDate())
            return widget

        elif f_type == "combo":
            widget = QComboBox()
            rel = field["relation"]
            if field.get("required") == False:
                widget.addItem("", userData=None)

            related_data = data_manager.get_all(rel["table"])

            for row in related_data:
                display_name = str(row[rel["name_col"]])
                record_id = row[rel["id_col"]]
                widget.addItem(display_name, userData=record_id)

            return widget
        elif f_type == "file":
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)

            line_edit = QLineEdit()
            line_edit.setReadOnly(True)
            line_edit.setPlaceholderText("Файл не выбран")

            target_folder = field.get("folder", "teams")
            btn_browse = QPushButton("Обзор...")
            btn_browse.clicked.connect(lambda: self.file_selection(line_edit, target_folder))

            layout.addWidget(line_edit)
            layout.addWidget(btn_browse)
            container.line_edit = line_edit
            return container

        else:
            return QLineEdit()

    def file_selection(self, line_edit, folder_name):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите эмблему", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            saved_name = data_manager.save_logo(file_path, folder_name)
            if saved_name:
                line_edit.setText(saved_name)

    def set_widget_value(self, widget, f_type, value):
        if value is None: return

        if f_type == "boolean":
            widget.setChecked(bool(value))
        elif f_type == "date":
            if isinstance(value, datetime.date):
                widget.setDate(QDate(value.year, value.month, value.day))
            elif isinstance(value, str):
                widget.setDate(QDate.fromString(value, "yyyy-MM-dd"))

        elif f_type == "combo":
            index = widget.findData(value)
            if index >= 0:
                widget.setCurrentIndex(index)
        elif f_type == "file" and hasattr(widget, "line_edit"):
            widget.line_edit.setText(str(value))
        else:
            widget.setText(str(value))

    def get_data(self):
        result = {}
        for col, widget in self.inputs.items():
            if hasattr(widget, "line_edit"):
                result[col] = widget.line_edit.text().strip()
            elif isinstance(widget, QCheckBox):
                result[col] = widget.isChecked()
            elif isinstance(widget, QDateEdit):
                result[col] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QComboBox):
                result[col] = widget.currentData()
            else:
                result[col] = widget.text().strip()
        return result

    def validate_data(self, data):
        for field in self.config["fields"]:
            col_name = field["column"]
            f_type = field["type"]
            label = field["label"]

            if f_type == "hidden":
                continue

            val = data.get(col_name)
            if field.get("required"):
                if val is None or str(val).strip() == "":
                    QMessageBox.warning(self, "Ошибка целостности", f"Поле '{label}' обязательно для заполнения!")
                    return False

            if f_type == "number" and val != "":
                try:
                    num_val = int(val)
                    if "min" in field and num_val < field["min"]:
                        QMessageBox.warning(self, "Ошибка целостности",
                                            f"Поле '{label}' не может быть меньше {field['min']}!")
                        return False
                    if "max" in field and num_val > field["max"]:
                        QMessageBox.warning(self, "Ошибка целостности",
                                            f"Поле '{label}' не может быть больше {field['max']}!")
                        return False
                except ValueError:
                    QMessageBox.warning(self, "Ошибка типа данных", f"Поле '{label}' должно быть числом!")
                    return False

        if self.config["title"] == "Матчи":
            if data.get("home_team_id") == data.get("away_team_id"):
                QMessageBox.warning(self, "Логическая аномалия",
                                    "Команда 'Хозяева' и команда 'Гости' не могут совпадать!")
                return False

        if self.config["title"] in ["Контракты", "Сезоны"]:
            if data.get("start_date") > data.get("end_date"):
                QMessageBox.warning(self, "Временная аномалия", "Дата начала не может быть позже даты окончания!")
                return False

        if self.config["title"] == "Матчи":
            match_date = data.get("match_date")
            season_id = data.get("season_id")
            if season_id:
                season_data = data_manager._get_one("seasons", "season_id", season_id)
                if season_data:
                    s_start = str(season_data["start_date"])
                    s_end = str(season_data["end_date"])

                    if not (s_start <= match_date <= s_end):
                        QMessageBox.warning(
                            self,
                            "Ошибка целостности",
                            f"Дата матча ({match_date}) выходит за рамки сезона!\n"
                            f"Сезон длится с {s_start} по {s_end}"
                        )
                        return False
        return True

    def update_teams_combos(self):
        season_box = self.inputs.get("season_id")
        home_combo = self.inputs.get("home_team_id")
        away_combo = self.inputs.get("away_team_id")

        if not (home_combo and away_combo):
            return

        season_id = season_box.currentData()

        cur_home = home_combo.currentData()
        cur_away = away_combo.currentData()

        for cb in [home_combo, away_combo]:
            cb.blockSignals(True)
            cb.clear()

        if season_id:
            teams = data_manager.get_teams(season_id)
            for t in sorted(teams, key=lambda x: x.get('name', '')):
                home_combo.addItem(t['name'], t['team_id'])
                away_combo.addItem(t['name'], t['team_id'])

        self.set_widget_value(home_combo, "combo", cur_home)
        self.set_widget_value(away_combo, "combo", cur_away)

        home_combo.blockSignals(False)
        away_combo.blockSignals(False)

    def accept(self):
        collected_data = self.get_data()
        if self.validate_data(collected_data):
            super().accept()