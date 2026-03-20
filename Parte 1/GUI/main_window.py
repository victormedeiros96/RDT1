from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import QThread, pyqtSlot

from GUI.main_widget import MainWidget
from Core.processing_worker import ProcessingWorker 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Processador de Imagens")
        self.resize(1000, 500)

        self._thread = None
        self._worker = None

        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)
        
        self.main_widget.start_requested.connect(self.handle_start_request)

    @pyqtSlot(str, str)
    def handle_start_request(self, input_folder, output_folder):
        self.main_widget.toggle_controls(False)
        self.statusBar().showMessage("Processo iniciado em segundo plano...")

        self._thread = QThread()
        self._worker = ProcessingWorker(input_folder, output_folder)
        self._worker.moveToThread(self._thread)

        self._worker.finished.connect(self._on_process_finished)
        self._worker.error.connect(self._on_process_error)
        self._thread.started.connect(self._worker.run)
        
        self._thread.finished.connect(self._thread.deleteLater)
        self._worker.finished.connect(self._thread.quit)
        
        self._thread.start()

    def _on_process_finished(self):
        self.statusBar().showMessage("Processo finalizado com sucesso!", 5000)
        self.main_widget.toggle_controls(True)
        
    def _on_process_error(self, error_message):
        QMessageBox.critical(self, "Erro no Processamento", error_message)
        self.main_widget.toggle_controls(True)

    def closeEvent(self, event):
        if self._thread and self._thread.isRunning():
            self._worker.stop() 
            self._thread.quit()
            self._thread.wait() 
        event.accept()