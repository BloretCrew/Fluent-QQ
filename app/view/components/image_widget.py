from PyQt6.QtCore import Qt, QThread, pyqtSignal, QByteArray
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from qfluentwidgets import SimpleCardWidget
import requests

class ImageWidget(SimpleCardWidget):
    """ Widget for displaying images in chat """
    def __init__(self, image_url, parent=None):
        super().__init__(parent)
        self.image_url = image_url
        self.setFixedSize(200, 200)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText("加载中...")
        self.image_label.setStyleSheet("color: gray;")
        
        layout.addWidget(self.image_label)
        
        # Load image asynchronously
        self.loadImage()
    
    def loadImage(self):
        """ Load image from URL """
        try:
            # Simple synchronous loading for now
            # TODO: Make this async with QThread
            response = requests.get(self.image_url, timeout=5)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                
                # Scale to fit
                scaled_pixmap = pixmap.scaled(
                    190, 190,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setText("")
                
                # Adjust widget size to image
                self.setFixedSize(scaled_pixmap.width() + 10, scaled_pixmap.height() + 10)
            else:
                self.image_label.setText("[图片加载失败]")
        except Exception as e:
            print(f"[ImageWidget] Failed to load image: {e}")
            self.image_label.setText("[图片加载失败]")
    
    def mousePressEvent(self, event):
        """ Click to view full size (TODO: implement full size viewer) """
        super().mousePressEvent(event)
        print(f"[ImageWidget] Clicked image: {self.image_url}")
