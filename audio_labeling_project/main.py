import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dark_style = """
        QWidget {
            background-color: #2b2b2b;
            color: #e0e0e0;
            font-family: 'Open Sans', 'Roboto', sans-serif;
        }
        QPushButton {
            background-color: #333;
            border: 1px solid #1abc9c;
            border-radius: 6px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #1abc9c;
            color: #ffffff;
        }
        QComboBox, QSlider, QProgressBar {
            background-color: #444;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 4px;
        }
    """
    app.setStyleSheet(dark_style)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
