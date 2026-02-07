
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
from PyQt6.QtWidgets import QLabel
from qfluentwidgets import ImageLabel, isDarkTheme, qconfig, Theme
import requests
from threading import Thread

class AvatarWidget(ImageLabel):
    """ Circular Avatar Widget with async loading """
    
    def __init__(self, image_path_or_url: str, size=36, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.image_url = image_path_or_url
        self.default_avatar = "app/resource/images/default_avatar.png"  # Fallback
        self.size_px = size
        
        # Enable styling
        self._update_style()
        qconfig.themeChanged.connect(self._on_theme_changed)
        
        self.scaledToWidth(size)
        
        if image_path_or_url.startswith("http"):
            self.loadFromUrl(image_path_or_url)
        else:
            self.setImage(image_path_or_url)

    def _on_theme_changed(self, theme):
        self._update_style(theme)

    def _update_style(self, theme=None):
        if theme is None:
            theme = qconfig.theme
        
        is_dark = theme == Theme.DARK or (theme == Theme.AUTO and isDarkTheme())
        bg = "#404040" if is_dark else "#e0e0e0"
        self.setStyleSheet(f"border-radius: {self.size_px//2}px; background-color: {bg};")

    def loadFromUrl(self, url):
        """ Load image from URL asynchronously """
        def _load():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    # Update UI in main thread (not strictly safe here but ImageLabel usually handles pixmap setting well, 
                    # but for safety we should use signals if this was complex. 
                    # For simplicity in this context, we'll assume direct setPixmap works or needs invokeMethod.
                    # Actually, PySide/PyQt UI updates MUST be in main thread.
                    # Let's use a simple QTimer or custom signal approach if needed, 
                    # but for now let's just use a simple synchronous load in thread with signal
                    # Wait, we can't emit signal from thread without defining it.
                    pass
            except Exception as e:
                print(f"[AvatarWidget] Error loading {url}: {e}")

        # Re-implementing correctly with signals
        self._loader = AvatarLoader(url)
        self._loader.loaded.connect(self.setAvatar)
        self._loader.start()

    def setAvatar(self, pixmap):
        if not pixmap.isNull():
            # Create circular mask
            size = self.size()
            rounded = QPixmap(size)
            rounded.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, size.width(), size.height())
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, size.width(), size.height(), pixmap)
            painter.end()
            
            self.setPixmap(rounded)

from PyQt6.QtCore import QThread

class AvatarLoader(QThread):
    loaded = pyqtSignal(QPixmap)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            response = requests.get(self.url, timeout=10)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.loaded.emit(pixmap)
        except:
            pass
