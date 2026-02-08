import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import setTheme
from app.common.config import config
from app.common.theme_manager import ThemeManager

def main():
    try:
        # Enable High DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        
        app = QApplication(sys.argv)
        
        # Apply theme at startup
        theme = config.get("theme")
        setTheme(theme)
        ThemeManager.apply_theme_patches(theme)
        
        from app.view.main_window import MainWindow
        w = MainWindow()
        w.show()
        
        sys.exit(app.exec())
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
