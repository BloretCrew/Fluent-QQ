import sys
import os
import unittest
from PyQt6.QtWidgets import QApplication

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.view.setting_interface import SettingInterface, FontSettingCard
from app.common.config import config

class TestSettingInterface(unittest.TestCase):
    def test_instantiation(self):
        """ Verify SettingInterface can be instantiated """
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
            
        # This triggers the code path that failed (creating FontSettingCard)
        w = SettingInterface()
        self.assertIsNotNone(w)
        self.assertIsInstance(w.fontCard, FontSettingCard)
        
        # Verify font items were populated
        count = w.fontCard.comboBox.count()
        self.assertTrue(count > 0, "Font list should not be empty")
        
        # Verify current value is selected
        current = w.fontCard.comboBox.currentText()
        self.assertEqual(current, config.chatFontFamily.value)

if __name__ == '__main__':
    unittest.main()
