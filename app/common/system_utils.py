
import winreg
from PyQt6.QtGui import QColor

def get_system_accent_color():
    """ Get Windows system accent color """
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r'Software\Microsoft\Windows\DWM')
        # Windows stores color as ABGR (0xAABBGGRR) in registry sometimes, or just ARGB
        # ColorizationColor is usually ARGB (0xAARRGGBB)
        # AccentColor might be different
        # Let's try to find a reliable source or just use a default
        value, regtype = winreg.QueryValueEx(key, 'ColorizationColor')
        winreg.CloseKey(key)
        
        # Convert to hex string
        # value is an integer. 
        # Example: 0xc40078d7 -> ARGB
        # We need QColor
        alpha = (value >> 24) & 0xff
        red = (value >> 16) & 0xff
        green = (value >> 8) & 0xff
        blue = value & 0xff
        
        return QColor(red, green, blue, alpha)
    except Exception as e:
        print(f"[Utils] Failed to get system accent color: {e}")
        return QColor("#009faa") # Default blue
