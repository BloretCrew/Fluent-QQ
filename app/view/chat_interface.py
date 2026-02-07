from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QVBoxLayout
from qfluentwidgets import SubtitleLabel, setFont

class ChatInterface(QFrame):
    """ Chat interface """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.label = SubtitleLabel("消息 - 正在连接...", self)
        
        self.setObjectName("chatInterface")
        self.layout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignCenter)
        setFont(self.label, 24)

    def setConnected(self, connected: bool):
        if connected:
            self.label.setText("消息 - 已连接")
        else:
            self.label.setText("消息 - 已断开 (重连中...)")

class ContactInterface(QFrame):
    """ Contact interface """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.label = SubtitleLabel("联系人", self)
        
        self.setObjectName("contactInterface")
        self.layout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignCenter)
        setFont(self.label, 24)
