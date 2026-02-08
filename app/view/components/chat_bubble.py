from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from qfluentwidgets import SimpleCardWidget, isDarkTheme, qconfig, Theme, RoundMenu, Action, FluentIcon as FIF, CaptionLabel

class ReplyQuote(QWidget):
    """ Widget to display reply reference """
    clicked = pyqtSignal()

    def __init__(self, reply_text="回复消息", parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 4, 8, 4)
        self.layout.setSpacing(4)
        
        self.bar = QWidget(self)
        self.bar.setFixedWidth(4)
        self.bar.setStyleSheet("background-color: #0078D4; border-radius: 2px;")
        
        self.content = CaptionLabel(reply_text, self)
        
        self.layout.addWidget(self.bar)
        self.layout.addWidget(self.content)
        self.layout.addStretch(1)
        
        self._update_style()
        qconfig.themeChanged.connect(self._on_theme_changed)

    def _on_theme_changed(self):
        self._update_style()

    def _update_style(self):
        if isDarkTheme():
            self.content.setStyleSheet("color: #CCCCCC;")
            self.setStyleSheet("ReplyQuote { background-color: rgba(255, 255, 255, 0.1); border-radius: 4px; } ReplyQuote:hover { background-color: rgba(255, 255, 255, 0.15); }")
        else:
            self.content.setStyleSheet("color: #666666;")
            self.setStyleSheet("ReplyQuote { background-color: rgba(0, 0, 0, 0.05); border-radius: 4px; } ReplyQuote:hover { background-color: rgba(0, 0, 0, 0.08); }")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)

class ReactionChip(QWidget):
    def __init__(self, icon, count, is_self_bubble=False, parent=None):
        super().__init__(parent)
        self.is_self_bubble = is_self_bubble
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(4)
        
        self.icon_label = QLabel(icon, self)
        self.count_label = QLabel(str(count), self)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.count_label)
        
        self._update_style()
        qconfig.themeChanged.connect(self._on_theme_changed)

    def _on_theme_changed(self):
        self._update_style()

    def _update_style(self):
        is_dark = isDarkTheme()
        
        if self.is_self_bubble:
            # On Blue background (Self)
            bg_color = "rgba(255, 255, 255, 0.2)"
            border_color = "rgba(255, 255, 255, 0.3)"
            text_color = "white"
        else:
            # On White/Gray background (Other)
            if is_dark:
                bg_color = "rgba(255, 255, 255, 0.1)"
                border_color = "rgba(255, 255, 255, 0.2)"
                text_color = "white"
            else:
                bg_color = "rgba(0, 0, 0, 0.08)"
                border_color = "rgba(0, 0, 0, 0.12)"
                text_color = "black"

        self.setStyleSheet(f"""
            ReactionChip {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 10px;
            }}
            QLabel {{
                font-size: 12px;
                background-color: transparent;
                color: {text_color};
                font-family: "Segoe UI Emoji", "Segoe UI", sans-serif;
            }}
        """)

class ChatBubble(SimpleCardWidget):
    """ Chat Message Bubble with Theme Support """
    
    reactRequested = pyqtSignal(str, str) # msg_id, emoji_id
    replyRequested = pyqtSignal(str) # msg_id
    recallRequested = pyqtSignal(str) # msg_id
    
    def __init__(self, message_id=None, is_self=False, parent=None):
        super().__init__(parent)
        self.message_id = message_id
        self.is_self = is_self
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(12, 8, 12, 8)
        self._layout.setSpacing(4)
        
        # Initial style update
        self._update_style()
        
        # Listen for theme changes
        qconfig.themeChanged.connect(self._on_theme_changed)

    def addWidget(self, widget):
        self._layout.addWidget(widget)
        
    def addLayout(self, layout):
        self._layout.addLayout(layout)
        
    def setReactions(self, reactions):
        """ 
        reactions: dict or list of (emoji_id, count, has_reacted) 
        For now assuming list of strings or simple dict
        """
        # Remove existing reaction widgets if any (usually at bottom)
        # TODO: Implement reaction display
        pass

    def setReply(self, reply_text, reply_id):
        # Add reply quote at top
        quote = ReplyQuote(reply_text, self)
        quote.clicked.connect(lambda: print(f"Jump to reply {reply_id}")) # TODO: Implement jump
        self._layout.insertWidget(0, quote)

    def contextMenuEvent(self, event):
        if not self.message_id:
            super().contextMenuEvent(event)
            return
            
        menu = RoundMenu(parent=self)
        
        # Reply Action
        reply_action = Action(FIF.EDIT, "回复", self)
        reply_action.triggered.connect(self._on_reply)
        menu.addAction(reply_action)
        
        menu.addSeparator()
        
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
            
    def _on_reply(self):
        if self.message_id:
            self.replyRequested.emit(str(self.message_id))
        
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

class ChatTextLabel(QLabel):
    """QLabel that delegates context menu to parent ChatBubble"""
    def contextMenuEvent(self, event):
        # Delegate to parent if it's a ChatBubble
        parent = self.parent()
        while parent:
            if isinstance(parent, ChatBubble):
                parent.contextMenuEvent(event)
                return
            parent = parent.parent()
        super().contextMenuEvent(event)
