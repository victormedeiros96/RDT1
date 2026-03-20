import sys
from PyQt6.QtWidgets import QApplication
from GUI.main_window import MainWindow

def load_stylesheet(app):
    try:
        with open("style.qss", "r") as file:
            style_sheet = file.read()
            app.setStyleSheet(style_sheet)
    except:
        pass
if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setStyle("fusion") 
    load_stylesheet(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())