
import unittest
import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

# Fix imports
sys.path.append('.')

from app.view.components.chat_bubble import ChatBubble

# Initialize App
app = QApplication(sys.argv)

class TestReplyUI(unittest.TestCase):
    def test_reply_quote_click(self):
        """ Test that clicking ReplyQuote emits signal from ChatBubble """
        bubble = ChatBubble(is_self=False, message_id="msg_123")
        
        print(f"DEBUG: bubble keys: {bubble.__dict__.keys()}")
        print(f"DEBUG: layout() = {bubble.layout()}")
        
        if hasattr(bubble, 'main_layout'):
            print(f"DEBUG: main_layout exists: {bubble.main_layout}")
        else:
            print("DEBUG: main_layout MISSING")

        # Set reply
        reply_id = "ref_456"
        bubble.setReply("Reply Content", reply_id)
        
        # Verify ReplyQuote exists
        self.assertTrue(hasattr(bubble, 'reply_widget'), "Reply widget not created")
        quote = bubble.reply_widget
        
        # Define slot
        self.signal_emitted = False
        self.received_id = None
        
        def on_reply_clicked(rid):
            self.signal_emitted = True
            self.received_id = rid
            
        bubble.replyClicked.connect(on_reply_clicked)
        
        # Simulate Click
        QTest.mouseClick(quote, Qt.MouseButton.LeftButton)
        
        # Check result
        self.assertTrue(self.signal_emitted, "Signal not emitted")
        self.assertEqual(self.received_id, reply_id)

if __name__ == '__main__':
    unittest.main()
