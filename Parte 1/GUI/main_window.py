# GUI/main_window.py

from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import QThread, pyqtSlot

from GUI.main_widget import MainWidget
# Mude o import para o novo worker
from Core.processing_worker import ProcessingWorker 

class MainWindow(QMainWindow):
    """
    Orquestrador que agora gerencia a execução do processamento em uma thread.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Processador de Imagens")
        self.resize(500, 300)

        self._thread = None
        self._worker = None

        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)
        
        self.main_widget.start_requested.connect(self.handle_start_request)

    @pyqtSlot(str, str)
    def handle_start_request(self, input_folder, output_folder):
        """Prepara e inicia o processamento em uma nova thread."""
        self.main_widget.toggle_controls(False)
        self.statusBar().showMessage("Processo iniciado em segundo plano...")

        self._thread = QThread()
        # Instancia o novo worker
        self._worker = ProcessingWorker(input_folder, output_folder)
        self._worker.moveToThread(self._thread)

        # Conecta os sinais
        self._worker.finished.connect(self._on_process_finished)
        self._worker.error.connect(self._on_process_error)
        self._thread.started.connect(self._worker.run)
        
        # O sinal finished da thread deve chamar quit() nela mesma
        self._thread.finished.connect(self._thread.deleteLater)
        self._worker.finished.connect(self._thread.quit)
        
        self._thread.start()

    def _on_process_finished(self):
        """Chamado quando o worker termina com sucesso."""
        self.statusBar().showMessage("Processo finalizado com sucesso!", 5000)
        self.main_widget.toggle_controls(True)
        
    def _on_process_error(self, error_message):
        """Chamado se o worker emitir um erro."""
        QMessageBox.critical(self, "Erro no Processamento", error_message)
        self.main_widget.toggle_controls(True)

    def closeEvent(self, event):
        """Garante que a thread seja encerrada ao fechar a janela."""
        if self._thread and self._thread.isRunning():
            # Idealmente, o worker teria um método para parar suavemente
            self._worker.stop() 
            self._thread.quit()
            self._thread.wait() # Espera a thread terminar
        event.accept()