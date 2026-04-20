import datetime
from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit,
                             QPushButton, QVBoxLayout, QCheckBox, QDateEdit, QComboBox, QMessageBox)
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
            f_type = field["type"]

            widget = self.create_widget(field)

            if self.current_data and col_name in self.current_data:
                value = self.current_data[col_name]
                self.set_widget_value(widget, f_type, value)

            form.addRow(field["label"] + ":", widget)
            self.inputs[col_name] = widget

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


        else:
            return QLineEdit()

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

        else:
            widget.setText(str(value))

    def get_data(self):
        result = {}
        for col, widget in self.inputs.items():
            if isinstance(widget, QCheckBox):
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

    def accept(self):
        collected_data = self.get_data()
        if self.validate_data(collected_data):
            super().accept()