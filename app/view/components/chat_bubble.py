from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtCore import pyqtSignal
from qfluentwidgets import SimpleCardWidget, isDarkTheme, qconfig, Theme, RoundMenu, Action, FluentIcon as FIF

class ChatBubble(SimpleCardWidget):
    """ Chat Message Bubble with Theme Support """
    
    recallRequested = pyqtSignal(str)
    reactRequested = pyqtSignal(str, str)
    
    def __init__(self, is_self, message_id=None, parent=None):
        super().__init__(parent)
        self.is_self = is_self
        self.message_id = message_id
        self._update_style()
        qconfig.themeChanged.connect(self._on_theme_changed)

    def contextMenuEvent(self, event):
        if not self.message_id:
            super().contextMenuEvent(event)
            return
            
        menu = RoundMenu(parent=self)
        
        # Reaction Submenu
        react_menu = RoundMenu("回应", parent=menu)
        react_menu.setIcon(FIF.HEART)
        
        # Common Reactions
        reactions = [
            ("👍", "76"), 
            ("❤️", "66"), 
            ("😂", "74"), 
            ("😮", "96"), 
            ("😭", "111")
        ]
        
        for icon, emoji_id in reactions:
            action = Action(icon, parent=react_menu)
            action.triggered.connect(lambda checked, eid=emoji_id: self._on_react(eid))
            react_menu.addAction(action)
            
        menu.addMenu(react_menu)

        if self.is_self:
            menu.addSeparator()
            recall_action = Action(FIF.DELETE, "撤回", self)
            recall_action.triggered.connect(self._on_recall)
            menu.addAction(recall_action)
            
        menu.exec(event.globalPos())
        
    def _on_react(self, emoji_id):
        if self.message_id:
            self.reactRequested.emit(str(self.message_id), str(emoji_id))
        
    def _on_recall(self):
        if self.message_id:
            self.recallRequested.emit(str(self.message_id))

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
