from PyQt6.QtWidgets import QVBoxLayout
from qfluentwidgets import SimpleCardWidget, isDarkTheme, qconfig, Theme

class ChatBubble(SimpleCardWidget):
    """ Chat Message Bubble with Theme Support """
    def __init__(self, is_self, parent=None):
        super().__init__(parent)
        self.is_self = is_self
        self._update_style()
        qconfig.themeChanged.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme):
        self._update_style(theme)

    def _update_style(self, theme=None):
        if theme is None:
            theme = qconfig.theme
            
        if self.is_self:
            # Self: Blue/Primary color background, White text
            self.setStyleSheet("""
                SimpleCardWidget {
                    background-color: #0078D4;
                    border: none;
                    border-radius: 8px;
                    border-top-right-radius: 0px;
                }
                SubtitleLabel, CaptionLabel {
                    color: white;
                }
            """)
        else:
            # Check if dark theme
            is_dark = theme == Theme.DARK or (theme == Theme.AUTO and isDarkTheme())
            
            if is_dark:
                bg = "#2d2d2d"
                border = "1px solid #3e3e3e"
                text = "white"
            else:
                bg = "#f9f9f9"
                border = "1px solid #e5e5e5"
                text = "black"
                
            self.setStyleSheet(f"""
                SimpleCardWidget {{
                    background-color: {bg};
                    border: {border};
                    border-radius: 8px;
                    border-top-left-radius: 0px;
                }}
                SubtitleLabel, CaptionLabel {{
                    color: {text};
                }}
            """)
