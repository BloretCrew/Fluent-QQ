import os
from PyQt6.QtCore import pyqtSignal
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, 
                            OptionsValidator, EnumSerializer, Theme)

class Config(QConfig):
    """ Configuration class """
    
    # Connection
    api_url = ConfigItem("Connection", "ApiUrl", "http://127.0.0.1:3000")
    ws_url = ConfigItem("Connection", "WsUrl", "ws://127.0.0.1:3001")
    token = ConfigItem("Connection", "Token", "")
    
    # Appearance
    themeMode = OptionsConfigItem(
        "Appearance", "Theme", Theme.AUTO, 
        OptionsValidator([Theme.LIGHT, Theme.DARK, Theme.AUTO]), EnumSerializer(Theme)
    )
    language = ConfigItem("Appearance", "Language", "zh_CN")

    def get(self, key, default=None):
        # Compatibility with old API
        if key == "api_url": return self.api_url.value
        if key == "ws_url": return self.ws_url.value
        if key == "token": return self.token.value
        if key == "theme": return self.themeMode.value
        if key == "language": return self.language.value
        return default

    def set(self, key, value):
        # Compatibility with old API
        if key == "theme":
            if isinstance(value, str):
                # Convert string to Theme enum
                value = Theme(value)
            qconfig.set(self.themeMode, value)

config = Config()
qconfig.load("config.json", config)
# Map themeChanged signal
config.themeChanged = config.themeMode.valueChanged
