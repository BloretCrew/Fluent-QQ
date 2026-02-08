import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel
from qfluentwidgets import Theme

# Mock or import necessary components
# Since we need to test UI components, we need a QApplication instance
app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

from app.view.components.chat_bubble import ChatBubble, ReactionChip

class TestReactionLogic(unittest.TestCase):
    
    def test_reaction_rendering(self):
        """ Test that reactions are correctly added to the bubble """
        bubble = ChatBubble(is_self=True, message_id="test_msg_1")
        
        # Test data covering different emojis
        reactions = [
            {"emoji_id": "76", "count": 1},   # Known emoji (Thumbs up)
            {"emoji_id": "999", "count": 5},  # Unknown/Custom emoji
            {"emoji_id": "66", "count": 2}    # Another known (Heart)
        ]
        
        bubble.setReactions(reactions)
        
        # Access the reaction widget (it's inside the bubble layout)
        # Structure: ChatBubble -> QVBoxLayout -> (content, reaction_widget)
        # The reaction_widget is added only if reactions exist.
        
        # Find the reaction widget using the attribute directly if available, or traversal
        reaction_widget = getattr(bubble, 'reaction_container', None)
        
        if not reaction_widget:
            # Fallback to traversal if attribute access fails (though it should be there)
            layout = bubble.layout()
            for i in range(layout.count()):
                item = layout.itemAt(i)
                widget = item.widget()
                if widget:
                    chips = widget.findChildren(ReactionChip)
                    if chips:
                        reaction_widget = widget
                        break
        
        self.assertIsNotNone(reaction_widget, "Reaction widget not found in bubble")
        
        # Get chips from the reaction widget
        found_chips = reaction_widget.findChildren(ReactionChip)
        self.assertEqual(len(found_chips), 3, "Should have 3 reaction chips")
        
        # Verify chip content
        # Chip 1: 76 -> 👍
        # ReactionChip is a QWidget, not a label. It has icon_label and count_label.
        chip1 = found_chips[0]
        self.assertEqual(chip1.icon_label.text(), "👍")
        self.assertEqual(chip1.count_label.text(), "1")
        
        # Chip 2: 999 -> ? (since len("999") == 3, and fallback logic returns "❓" for len <= 3 not in map)
        chip2 = found_chips[1]
        self.assertEqual(chip2.icon_label.text(), "❓")
        self.assertEqual(chip2.count_label.text(), "5")
        
        # Chip 3: 66 -> ❤️
        chip3 = found_chips[2]
        self.assertEqual(chip3.icon_label.text(), "❤️")
        self.assertEqual(chip3.count_label.text(), "2")
        
    def test_reaction_visibility(self):
        """ Test visibility toggling """
        bubble = ChatBubble(is_self=False, message_id="test_msg_2")
        bubble.setReactions([])
        
        # Should not have reaction widget visible or present
        layout = bubble.layout()
        has_chips = False
        for i in range(layout.count()):
            item = layout.itemAt(i)
            w = item.widget()
            if w and w.findChildren(ReactionChip):
                has_chips = True
                break
        self.assertFalse(has_chips, "Should not have chips for empty reactions")

if __name__ == '__main__':
    unittest.main()
