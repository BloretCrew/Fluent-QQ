
import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from app.view.components.chat_bubble import ChatBubble

# Mock config
from qfluentwidgets import qconfig
from app.common.config import config

def test_chat_bubble_layout():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        
    parent = QWidget()
    
    # Simulate chat_interface.py logic
    bubble = ChatBubble(is_self=True, message_id="123", parent=parent)
    
    l = bubble.layout()
    print(f"DEBUG: bubble.layout() = {l}")
    print(f"DEBUG: type(l) = {type(l)}")
    print(f"DEBUG: bool(l) = {bool(l)}")
    
    # Fixed code:
    bubble_layout = bubble.layout()
    if not bubble_layout:
        bubble_layout = QVBoxLayout(bubble)
        print("Created new layout")
    else:
        print("Reused existing layout")
        
    bubble_layout.setContentsMargins(12, 10, 12, 10)
    
    # Check if we get warnings (captured via stderr usually, but here we just check logic)
    # If we tried to create a new layout on top of existing one, PyQt prints warning to console.
    
    print("Test finished without crash. Check console for QLayout warnings.")

if __name__ == "__main__":
    test_chat_bubble_layout()
