# app/common/theme_manager.py
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from qfluentwidgets import Theme, qconfig, isDarkTheme

class ThemeManager:
    @staticmethod
    def apply_theme_patches(theme: Theme):
        """ 
        Apply manual patches for standard Qt widgets to match Fluent UI theme.
        This handles cases where standard QWidget, QLabel, etc. don't pick up 
        the qfluentwidgets theme automatically.
        """
        try:
            is_dark = (theme == Theme.DARK) or (theme == Theme.AUTO and isDarkTheme())
            
            if is_dark:
                # Dark Mode Patches
                palette = QApplication.palette()
                palette.setColor(QPalette.ColorRole.Window, QColor("#2e2e2e"))
                palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
                palette.setColor(QPalette.ColorRole.Base, QColor("#1e1e1e"))
                palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#2e2e2e"))
                palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
                palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
                palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
                palette.setColor(QPalette.ColorRole.Button, QColor("#3a3a3a"))
                palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
                palette.setColor(QPalette.ColorRole.BrightText, QColor("#ff0000"))
                palette.setColor(QPalette.ColorRole.Link, QColor("#2a82da"))
                palette.setColor(QPalette.ColorRole.Highlight, QColor("#2a82da"))
                palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
                QApplication.setPalette(palette)
                
                # Global Stylesheet for standard widgets
                # Note: We target specific widgets to avoid breaking custom Fluent widgets
                QApplication.instance().setStyleSheet("""
                    QWidget { background-color: #2e2e2e; color: #ffffff; }
                    QScrollArea { background-color: transparent; border: none; }
                    QScrollArea > QWidget > QWidget { background-color: transparent; }
                    /* Exclude Fluent widgets from generic styling if possible, or ensure specificity */
                    QPushButton { background-color: #3a3a3a; border: 1px solid #444444; color: #ffffff; border-radius: 4px; padding: 5px; }
                    QPushButton:hover { background-color: #4a4a4a; }
                    QPushButton:pressed { background-color: #5a5a5a; }
                    QLineEdit { background-color: #3a3a3a; border: 1px solid #444444; color: #ffffff; border-radius: 4px; }
                    QLabel { color: #ffffff; }
                """)
            else:
                # Light Mode - Reset to defaults
                QApplication.instance().setStyleSheet("") 
        except Exception as e:
            print(f"[ThemeManager] Failed to apply theme patches: {e}")
            return
