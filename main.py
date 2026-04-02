import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from qt_material import apply_stylesheet


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    apply_stylesheet(app, theme='dark_teal.xml')
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()