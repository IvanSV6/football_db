from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QHBoxLayout, QHeaderView, QMessageBox)
from config import TABLE_CONFIG
from ui.universal_dialog import UniversalDialog
from controllers.data_manager import data_manager
from controllers.session import session


class GenericTableTab(QWidget):
    def __init__(self, table_name):
        super().__init__()
        self.table_name = table_name
        self.config = TABLE_CONFIG[table_name]
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Изменить")
        self.btn_delete = QPushButton("Удалить")
        self.btn_refresh = QPushButton("Обновить")

        self.btn_add.clicked.connect(self.on_add)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_refresh.clicked.connect(self.refresh_data)

        role = session.current_role
        self.btn_add.setVisible(role in ["admin", "manager"])
        self.btn_edit.setVisible(role in ["admin", "manager"])
        self.btn_delete.setVisible(role == "admin")

        self.btn_layout.addWidget(self.btn_add)
        self.btn_layout.addWidget(self.btn_edit)
        self.btn_layout.addWidget(self.btn_delete)
        self.btn_layout.addWidget(self.btn_refresh)
        self.btn_layout.addStretch()
        layout.addLayout(self.btn_layout)

        self.table = QTableWidget()
        headers = [f["label"] for f in self.config["fields"] if f["type"] != "hidden"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

    def refresh_data(self):
        data = data_manager.get_all(self.table_name)
        self.table.setRowCount(0)
        rel_caches = {}
        for field in self.config["fields"]:
            if field.get("type") == "combo":
                rel = field["relation"]
                related_rows = data_manager.get_all(rel["table"])
                rel_caches[field["column"]] = {
                    row[rel["id_col"]]: row[rel["name_col"]]
                    for row in related_rows
                }

        for row_idx, row_data in enumerate(data):
            self.table.insertRow(row_idx)
            visible_col_idx = 0

            for field in self.config["fields"]:
                if field["type"] == "hidden":
                    continue

                col_name = field["column"]
                raw_value = row_data.get(col_name)

                if field.get("type") == "combo" and col_name in rel_caches:
                    display_value = rel_caches[col_name].get(raw_value, raw_value)
                else:
                    display_value = raw_value

                item = QTableWidgetItem(str(display_value) if display_value is not None else "")
                self.table.setItem(row_idx, visible_col_idx, item)
                visible_col_idx += 1

    def on_add(self):
        dialog = UniversalDialog(self.table_name)
        if dialog.exec():
            data = dialog.get_data()
            if data_manager.add_record(self.table_name, data):
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить запись")

    def on_edit(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите строку для редактирования")
            return

        all_data = data_manager.get_all(self.table_name)
        record = all_data[selected_row]
        id_col = data_manager._get_id_column(self.table_name)
        record_id = record[id_col]

        dialog = UniversalDialog(self.table_name, current_data=record)
        if dialog.exec():
            new_data = dialog.get_data()
            if data_manager.up_record(self.table_name, record_id, new_data):
                self.refresh_data()

    def on_delete(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите строку для удаления")
            return

        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить запись?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            all_data = data_manager.get_all(self.table_name)
            record_id = all_data[selected_row][data_manager._get_id_column(self.table_name)]

            if data_manager.del_record(self.table_name, record_id):
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить запись")