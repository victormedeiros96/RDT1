import sys

def run_gui_application():
    """Inicia a aplicação gráfica PyQt."""
    from PyQt6.QtWidgets import QApplication
    from GUI.main_window import MainWindow
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    run_gui_application()