from PyQt6.QtCore import QObject, pyqtSignal
from Core.processing_script import ImageProcessor

class ProcessingWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, input_folder, output_folder, batch_size=20):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.batch_size = batch_size
        self.is_running = True

    def run(self):
        try:
            processor = ImageProcessor(self.input_folder, self.output_folder)
            for side in ['left', 'right']:
                if not self.is_running:
                    break
                processor.process_images_for_side(side, images_per_concat=self.batch_size)
        except Exception as e:
            self.error.emit(f"Ocorreu um erro durante o processamento: {e}")
        finally:
            if self.is_running:
                self.finished.emit()
    def stop(self):
        self.is_running = False