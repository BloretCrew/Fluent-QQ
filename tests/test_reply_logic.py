
import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.common.history_manager import HistoryManager

class TestReplyLogic(unittest.TestCase):
    def test_get_message_by_id(self):
        """ Test retrieval of messages by ID """
        # We need to mock the DB or ensure it handles missing files gracefully
        hm = HistoryManager(user_id="test_user")
        
        # Test non-existent
        msg = hm.get_message_by_id("non_existent_id")
        self.assertIsNone(msg)
        
        # Test saving and retrieving
        test_msg = {
            "message_id": "test_msg_1",
            "sender": {"user_id": "123"},
            "message": "Hello"
        }
        hm.save_message("target_1", False, test_msg)
        
        retrieved = hm.get_message_by_id("test_msg_1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.get("message"), "Hello")

if __name__ == '__main__':
    unittest.main()
