import datetime
from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit,
                             QPushButton, QVBoxLayout, QCheckBox, QDateEdit, QComboBox)
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