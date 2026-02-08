import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from qfluentwidgets import setTheme, Theme

from app.view.components.chat_bubble import ChatBubble

if __name__ == '__main__':
    app = QApplication(sys.argv)
    setTheme(Theme.LIGHT)
    
    w = QWidget()
    w.resize(400, 300)
    layout = QVBoxLayout(w)
    
    # Self bubble with reactions
    b1 = ChatBubble(is_self=True, message_id="1")
    # Simulate adding content
    from PyQt6.QtWidgets import QLabel
    b1.layout().addWidget(QLabel("Hello World (Self)", b1))
    
    reactions1 = [
        {"emoji_id": "76", "count": 1},
        {"emoji_id": "66", "count": 2},
        {"emoji_id": "999", "count": 5} # Unknown
    ]
    b1.setReactions(reactions1)
    layout.addWidget(b1)
    
    # Other bubble with reactions
    b2 = ChatBubble(is_self=False, message_id="2")
    b2.layout().addWidget(QLabel("Hello World (Other)", b2))
    
    reactions2 = [
        {"emoji_id": "74", "count": 10},
        {"emoji_id": "111", "count": 1}
    ]
    b2.setReactions(reactions2)
    layout.addWidget(b2)
    
    w.show()
    sys.exit(app.exec())
