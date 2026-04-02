from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QHeaderView, QHBoxLayout, QComboBox

class TournamentTable(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Основной вертикальный слой
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 1. Заголовок и фильтры
        header_layout = QHBoxLayout()

        title = QLabel("Турнирная таблица")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00bcd4;")

        self.season_box = QComboBox()
        self.season_box.setFixedWidth(200)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Выбрать сезон:"))
        header_layout.addWidget(self.season_box)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "№", "Команда", "И", "В", "Н", "П", "Мячи", "Очки"
        ])

        # Делаем таблицу красивой
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Растягиваем на всё окно
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # № — по контенту

        self.table.verticalHeader().setVisible(False)  # Прячем стандартные номера строк
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Только чтение
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # Выделять всю строку

        layout.addWidget(self.table)