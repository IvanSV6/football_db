from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout
from config import TABLE_CONFIG


class UniversalDialog(QDialog):
    def __init__(self, table_name, parent=None):
        super().__init__(parent)
        self.config = TABLE_CONFIG[table_name]
        self.inputs = {}
        self.setWindowTitle(f"Редактирование: {self.config['title']}")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        for field in self.config["fields"]:
            if field["type"] == "hidden": continue

            line_edit = QLineEdit()
            form.addRow(field["label"] + ":", line_edit)
            self.inputs[field["column"]] = line_edit

        layout.addLayout(form)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

    def get_data(self):
        return {col: widget.text() for col, widget in self.inputs.items()}