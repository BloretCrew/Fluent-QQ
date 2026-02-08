
import unittest
import sys
import os
from PyQt6.QtGui import QFontDatabase

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.common.config import Config, config, qconfig

class TestFontConfig(unittest.TestCase):
    def test_font_config_defaults(self):
        """ Test default font configuration """
        # Should default to Microsoft YaHei or first available
        self.assertEqual(config.chatFontFamily.value, "Microsoft YaHei")

    def test_font_config_update(self):
        """ Test updating font configuration """
        original = config.chatFontFamily.value
        
        # Change to a different font
        new_font = "Segoe UI"
        config.set("chatFontFamily", new_font)
        self.assertEqual(config.chatFontFamily.value, new_font)
        
        # Restore
        config.set("chatFontFamily", original)

    def test_system_fonts_availability(self):
        """ Verify we can list system fonts """
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
            
        families = QFontDatabase.families()
        self.assertTrue(len(families) > 0)
        
        # Check if commonly used fonts exist (optional, depends on OS)
        # print(f"Available fonts: {families[:5]}...")

if __name__ == '__main__':
    unittest.main()
