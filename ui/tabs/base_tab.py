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

        self.btn_add.clicked.connect(self.on_add)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)

        role = session.current_role
        self.btn_add.setVisible(role in ["admin", "manager"])
        self.btn_edit.setVisible(role in ["admin", "manager"])
        self.btn_delete.setVisible(role == "admin")

        self.btn_layout.addWidget(self.btn_add)
        self.btn_layout.addWidget(self.btn_edit)
        self.btn_layout.addWidget(self.btn_delete)
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

        for row_idx, row_data in enumerate(data):
            self.table.insertRow(row_idx)

            visible_col_idx = 0
            for field in self.config["fields"]:
                if field["type"] == "hidden":
                    continue
                column_name = field["column"]
                value = row_data.get(column_name, "")

                self.table.setItem(row_idx, visible_col_idx, QTableWidgetItem(str(value)))
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
        selected = self.table.currentRow()
        if selected < 0: return
        # Логика редактирования...
        pass

    def on_delete(self):
        # Логика удаления по ID...
        pass