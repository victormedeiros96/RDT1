import sys
def load_stylesheet(app):
    try:
        with open("style.qss", "r") as file:
            style_sheet = file.read()
            app.setStyleSheet(style_sheet)
    except:
        pass
def run_gui_application():
    from PyQt6.QtWidgets import QApplication
    from GUI.main_window import MainWindow
    
    app = QApplication(sys.argv)
    QApplication.setStyle("fusion") 
    load_stylesheet(app)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    run_gui_application()