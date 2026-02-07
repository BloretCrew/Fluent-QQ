from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QVBoxLayout
from qfluentwidgets import SubtitleLabel, setFont

class ContactInterface(QFrame):
    """ Contact interface """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.label = SubtitleLabel("联系人", self)
        
        self.setObjectName("contactInterface")
        self.layout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignCenter)
        setFont(self.label, 24)
