from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class BannerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent; border-bottom: 1px solid #CCCCCC;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)

        logo_nro_pixmap = QPixmap("images/logo_nro.png")
        logo_nro_label = QLabel()
        logo_nro_label.setPixmap(logo_nro_pixmap.scaledToHeight(100, Qt.TransformationMode.SmoothTransformation))
        
        logo_van_pixmap = QPixmap("images/logo2.png")
        logo_van_label = QLabel()
        logo_van_label.setPixmap(logo_van_pixmap.scaledToHeight(100, Qt.TransformationMode.SmoothTransformation))
        
        
        logo_antt_pixmap = QPixmap("images/logo_antt.svg")
        logo_antt_label = QLabel()
        logo_antt_label.setPixmap(logo_antt_pixmap.scaledToHeight(80, Qt.TransformationMode.SmoothTransformation))

        layout.addWidget(logo_nro_label)
        layout.addStretch()
        layout.addWidget(logo_van_label)
        layout.addStretch()        
        layout.addWidget(logo_antt_label)