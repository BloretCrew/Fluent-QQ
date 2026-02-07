import os
import json
from PyQt6.QtCore import pyqtSignal
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, 
                            OptionsValidator, EnumSerializer, Theme)
from enum import Enum

class ImagePreviewMode(Enum):
    """ Image Preview Mode """
    QUICKLOOK = "QuickLook"
    SYSTEM_DEFAULT = "System Default"

class Config(QConfig):
    """ Configuration class """
    
    # Connection
    api_url = ConfigItem(None, "api_url", "http://127.0.0.1:3000")
    ws_url = ConfigItem(None, "ws_url", "ws://127.0.0.1:3001")
    token = ConfigItem(None, "token", "")
    
    # Appearance
    themeMode = OptionsConfigItem(
        None, "theme", Theme.AUTO, 
        OptionsValidator([Theme.LIGHT, Theme.DARK, Theme.AUTO]), EnumSerializer(Theme)
    )
    
    # Behavior
    imagePreviewMode = OptionsConfigItem(
        None, "imagePreviewMode", ImagePreviewMode.QUICKLOOK,
        OptionsValidator(ImagePreviewMode), EnumSerializer(ImagePreviewMode)
    )
    
    language = ConfigItem(None, "language", "zh_CN")

    def get(self, key, default=None):
        if key == "api_url": return self.api_url.value
        if key == "ws_url": return self.ws_url.value
        if key == "token": return self.token.value
        if key == "theme": return self.themeMode.value
        if key == "imagePreviewMode": return self.imagePreviewMode.value
        if key == "language": return self.language.value
        return default

    def set(self, key, value):
        if key == "theme":
            if isinstance(value, str):
                try: value = Theme(value)
                except: value = Theme.AUTO
            qconfig.set(self.themeMode, value)
        elif key == "imagePreviewMode":
            if isinstance(value, str):
                try: value = ImagePreviewMode(value)
                except: value = ImagePreviewMode.QUICKLOOK
            qconfig.set(self.imagePreviewMode, value)
        elif hasattr(self, key):
            item = getattr(self, key)
            if isinstance(item, ConfigItem):
                qconfig.set(item, value)

config = Config()
config_path = os.path.abspath("config.json")

def load_config():
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Support both flat and nested "null" structure
                source = data.get("null", data) if isinstance(data.get("null"), dict) else data
                
                if "api_url" in source: config.api_url.value = source["api_url"]
                if "ws_url" in source: config.ws_url.value = source["ws_url"]
                if "token" in source: config.token.value = source["token"]
                if "theme" in source:
                    try: config.themeMode.value = Theme(source["theme"])
                    except: pass
                if "imagePreviewMode" in source:
                    try: config.imagePreviewMode.value = ImagePreviewMode(source["imagePreviewMode"])
                    except: pass
                if "language" in source: config.language.value = source["language"]
                
                print(f"[Config] Loaded: API={config.api_url.value}, WS={config.ws_url.value}, Token={'***' if config.token.value else 'None'}")
        except Exception as e:
            print(f"[Config] Load error: {e}")

load_config()
qconfig.load(config_path, config)
config.themeChanged = config.themeMode.valueChanged
