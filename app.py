import sys
from PySide6.QtWidgets import QApplication
from ui_main import MusicPlayerWindow


def main():
    app = QApplication(sys.argv)
    window = MusicPlayerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()