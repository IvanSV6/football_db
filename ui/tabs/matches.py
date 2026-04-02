from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QHeaderView, QHBoxLayout, QComboBox, QTableWidgetItem
from PyQt6.QtCore import Qt, QDate

class MatchesTable(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()

        title = QLabel("Календарь матчей")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00bcd4;")

        self.season_box = QComboBox()
        self.season_box.setFixedWidth(200)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Выбрать сезон:"))
        header_layout.addWidget(self.season_box)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Дата", "Тур", "Хозяева", "Счет", "Гости", "Стадион"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Растягиваем на всё окно
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        self.table.verticalHeader().setVisible(False)  # Прячем стандартные номера строк
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Только чтение
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # Выделять всю строку

        layout.addWidget(self.table)

        self.load_demo_data()



    def load_demo_data(self):
        # Пример данных, которые в будущем придут из БД
        data = [
            ("20.03.2026", "Спартак", "2 : 1", "Зенит", "Лужники", "Завершен"),
            ("25.03.2026", "ЦСКА", "0 : 0", "Динамо", "ВЭБ Арена", "Завершен"),
            ("05.04.2026", "Локомотив", "- : -", "Спартак", "РЖД Арена", "Ожидается"),
        ]

        self.table.setRowCount(len(data))
        for row, match in enumerate(data):
            for col, value in enumerate(match):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Маленький UX-хак: подсветим счет жирным
                if col == 2:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

                self.table.setItem(row, col, item)