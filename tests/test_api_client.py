import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.common.api_client import NapCatClient

class TestApiClient(unittest.TestCase):
    def test_get_group_member_list(self):
        """ Verify get_group_member_list exists and calls API correctly """
        client = NapCatClient()
        client.call_api = MagicMock(return_value={"status": "ok"})
        
        # Test valid call
        client.get_group_member_list("123456")
        client.call_api.assert_called_with("get_group_member_list", {"group_id": 123456, "no_cache": False})
        
        # Test invalid ID
        client.get_group_member_list(None)
        # Should not call API again (call_api call count should still be 1)
        self.assertEqual(client.call_api.call_count, 1)

if __name__ == '__main__':
    unittest.main()
