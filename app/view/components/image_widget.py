from PyQt6.QtCore import Qt, QThread, pyqtSignal, QByteArray
from PyQt6.QtGui import QPixmap, QDesktopServices
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QLabel, QVBoxLayout
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from qfluentwidgets import SimpleCardWidget
import requests
import os
import tempfile
import sys
from ...common.config import config, ImagePreviewMode
# from .image_preview_window import ImagePreviewWindow
import subprocess

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
        """ Load image from URL or local path """
        try:
            pixmap = QPixmap()
            success = False
            
            # Handle local file or file:// protocol
            if self.image_url.startswith("file://") or not self.image_url.startswith("http"):
                local_path = self.image_url
                if local_path.startswith("file:///"):
                    local_path = local_path[8:]
                
                if os.path.exists(local_path):
                    success = pixmap.load(local_path)
            else:
                # Simple synchronous loading for now
                # TODO: Make this async with QThread
                response = requests.get(self.image_url, timeout=5)
                if response.status_code == 200:
                    success = pixmap.loadFromData(response.content)

            if success:
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
        """ Click to view full size """
        super().mousePressEvent(event)
        
        mode = config.get("imagePreviewMode")
        print(f"[ImageWidget] Clicked. Mode: {mode}")
        
        if mode == ImagePreviewMode.QUICKLOOK:
            self.showQuickLook()
        else:
            self.openSystemDefault()

    def _get_local_filepath(self):
        """ Get local filepath, downloading if necessary """
        url = self.image_url
        if url.startswith("file:///"):
            return url[8:]
        
        if not url.startswith("http"):
            return url
            
        try:
            # Simple temp file caching
            # In production, use a proper cache directory and hashing
            suffix = ".jpg"
            if ".png" in self.image_url: suffix = ".png"
            elif ".gif" in self.image_url: suffix = ".gif"
            
            # Create temp file
            # We don't delete it immediately so external apps can open it
            # OS will clean up temp dir eventually, or we should manage it
            fd, filepath = tempfile.mkstemp(suffix=suffix)
            os.close(fd)
            
            print(f"[ImageWidget] Downloading to temp: {filepath}")
            response = requests.get(self.image_url, timeout=10)
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            return filepath
        except Exception as e:
            print(f"[ImageWidget] Failed to download image: {e}")
            return None

    def showQuickLook(self):
        """ Show using external QuickLook application via PowerShell script """
        filepath = self._get_local_filepath()
        if not filepath: return
        
        try:
            # Resolve script path
            # Current file: app/view/components/image_widget.py
            # Script: app/common/launch_quicklook.ps1
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # ../../common/launch_quicklook.ps1
            script_path = os.path.abspath(os.path.join(current_dir, "../../common/launch_quicklook.ps1"))
            
            if not os.path.exists(script_path):
                print(f"[ImageWidget] Script not found: {script_path}")
                self.openSystemDefault()
                return

            # Run PowerShell script
            # Use PowerShell to run the script which handles path resolution and execution
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script_path, filepath]
            
            print(f"[ImageWidget] Running: {cmd}")
            # Use subprocess.Popen to run without blocking UI
            # creationflags=0x08000000 (CREATE_NO_WINDOW) helps hide the console window on Windows
            creation_flags = 0x08000000 if sys.platform == 'win32' else 0
            subprocess.Popen(cmd, creationflags=creation_flags)
            
        except Exception as e:
            print(f"[ImageWidget] Failed to run QuickLook script: {e}")
            self.openSystemDefault()

    def openSystemDefault(self):
        """ Open with system default viewer """
        try:
            filepath = self._get_local_filepath()
            if not filepath: return
            
            print(f"[ImageWidget] Opening: {filepath}")
            QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
            
        except Exception as e:
            print(f"[ImageWidget] Failed to open system viewer: {e}")
