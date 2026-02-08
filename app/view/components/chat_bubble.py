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
    
    recallRequested = pyqtSignal(str)
    reactRequested = pyqtSignal(str, str)
    replyRequested = pyqtSignal(str) # message_id
    replyClicked = pyqtSignal(str) # reply_id
    
    def __init__(self, is_self, message_id=None, parent=None):
        super().__init__(parent)
        self.is_self = is_self
        self.message_id = message_id
        
        # Ensure layout exists
        if self.layout() is None:
            # print("DEBUG: Creating new QVBoxLayout in __init__")
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
            self.main_layout.setContentsMargins(12, 8, 12, 8)
        else:
            # print(f"DEBUG: Layout already exists: {self.layout()}")
            self.main_layout = self.layout()
            
        self._update_style()
        qconfig.themeChanged.connect(self._on_theme_changed)

    def setReply(self, reply_text, reply_id=None):
        """ Set reply quote """
        layout = self.layout()
        if layout is None and hasattr(self, 'main_layout'):
            layout = self.main_layout
            
        if layout is None:
            # Fallback: try to find layout or create one
            layout = self.findChild(QVBoxLayout)
            if layout is None:
                layout = QVBoxLayout(self)
                self.setLayout(layout)
                self.main_layout = layout
        
        # Check if already exists
        if hasattr(self, 'reply_widget'):
            layout.removeWidget(self.reply_widget)
            self.reply_widget.deleteLater()
        
        self.reply_widget = ReplyQuote(reply_text, self)
        if reply_id:
            self.reply_widget.clicked.connect(lambda: self.replyClicked.emit(str(reply_id)))
            
        # Insert at top (index 0)
        layout.insertWidget(0, self.reply_widget)

    def setReactions(self, reactions):
        """
        Display reactions below the message
        reactions: list of dict, e.g. [{"emoji_id": "76", "count": 1}, ...]
        """
        layout = getattr(self, 'main_layout', self.layout())
        
        if layout is None:
            layout = self.layout()
            
        if layout is None:
            print(f"DEBUG: No layout found in ChatBubble instance {id(self)}")
            # Attempt to recover
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
            layout = self.main_layout
            
        # Remove existing reaction container if exists
        if hasattr(self, 'reaction_container'):
            layout.removeWidget(self.reaction_container)
            self.reaction_container.deleteLater()
            del self.reaction_container
            
        if not reactions:
            return
            
        self.reaction_container = QWidget(self)
        self.reaction_container.setObjectName("reaction_container")
        self.reaction_container.setStyleSheet("background-color: transparent; border: none;")
        
        r_layout = QHBoxLayout(self.reaction_container)
        r_layout.setContentsMargins(0, 4, 0, 0)
        r_layout.setSpacing(4)
        
        for r in reactions:
            emoji_id = str(r.get("emoji_id"))
            count = r.get("count", 1)
            icon = self._get_emoji_char(emoji_id)
            
            chip = ReactionChip(icon, count, self.is_self, self.reaction_container)
            r_layout.addWidget(chip)
            
        r_layout.addStretch(1)
        layout.addWidget(self.reaction_container)
        print("DEBUG: reaction_container added to layout")

    def _get_emoji_char(self, emoji_id):
        mapping = {
            "76": "👍", "66": "❤️", "74": "😂", "96": "😮", "111": "😭",
            "37": "😎", "27": "😅", "118": "😵", "112": "😡", "14": "微笑",
            "124": "🙏", "179": "💩", "109": "😓", "13": "呲牙",
            # Add more common ones or fallback
        }
        # If not in mapping, try to be helpful
        # Some IDs might be system IDs that don't map well to unicode.
        # Fallback: if we don't know it, we can return the ID if it's weird, or a generic symbol.
        # But showing "❓" is better than nothing.
        # Let's check if it's a known "OK" gesture or similar.
        
        return mapping.get(emoji_id, f"[{emoji_id}]" if len(emoji_id) > 3 else "❓")

    def contextMenuEvent(self, event):
        if not self.message_id:
            super().contextMenuEvent(event)
            return
            
        menu = RoundMenu(parent=self)
        
        # Reply Action
        reply_action = Action(FIF.REPLY, "回复", self)
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
