from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from qfluentwidgets import (FluentWindow, NavigationItemPosition, FluentIcon as FIF,
                            setTheme, Theme, setThemeColor, MessageBox, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF

from .chat_interface import ChatInterface
from .contact_interface import ContactInterface
from .setting_interface import SettingInterface
from ..common.config import config
from ..common.api_client import client
from ..common.system_utils import get_system_accent_color
from ..common.theme_manager import ThemeManager

class MainWindow(FluentWindow):
    """ Main window """
    def __init__(self):
        super().__init__()
        
        # 1. Sync with system accent color (Like Bloret)
        try:
            accent_color = get_system_accent_color()
            print(f"[MainWindow] System Accent Color: {accent_color.name()}")
            setThemeColor(accent_color)
        except Exception as e:
            print(f"[MainWindow] Failed to set theme color: {e}")

        # 2. Force Theme Update (Like Bloret)
        # This ensures that even if config says Auto, we strictly enforce the correct state
        if isDarkTheme():
            setTheme(Theme.AUTO)
            # Re-apply patches to ensure they stick
            ThemeManager.apply_theme_patches(Theme.DARK)
        
        # Create sub interfaces
        self.chatInterface = ChatInterface(self)
        self.contactInterface = ContactInterface(self)
        self.settingInterface = SettingInterface(self)
        
        self.initNavigation()
        self.initWindow()
        self.initSystemTray()

        # Connect signals
        client.connected.connect(lambda: self.chatInterface.setConnected(True))
        client.disconnected.connect(lambda: self.chatInterface.setConnected(False))
        client.messageReceived.connect(self.chatInterface.addMessage)
        
        # Connect contact interface to chat
        self.contactInterface.openChatRequested.connect(self.openChatFromContact)
        
        # Start connection
        client.start_ws()
    
    def openChatFromContact(self, target_id, name, is_group):
        """ Open chat from contact interface and switch to chat tab """
        # Switch to chat interface
        self.switchTo(self.chatInterface)
        # Open the chat
        self.chatInterface.openChat(target_id, name, is_group)

    def initNavigation(self):
        self.addSubInterface(self.chatInterface, FIF.MESSAGE, "消息")
        self.addSubInterface(self.contactInterface, FIF.PEOPLE, "联系人")
        
        self.addSubInterface(self.settingInterface, FIF.SETTING, "设置", NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(1000, 700)
        self.setWindowIcon(QIcon("qq.png"))
        self.setWindowTitle("Fluent QQ")
        
        # Theme is applied in main.py to avoid runtime issues
        # config.themeChanged.connect(self.applyTheme)

    def applyTheme(self, theme):
        setTheme(theme)
    
    def initSystemTray(self):
        """ Initialize system tray icon """
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("qq.png"))
        self.tray_icon.setToolTip("Fluent QQ")
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self.showNormal)
        show_action.triggered.connect(self.activateWindow)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        
        # Single click to show/hide
        self.tray_icon.activated.connect(self.onTrayIconActivated)
        
        self.tray_icon.show()
    
    def onTrayIconActivated(self, reason):
        """ Handle tray icon activation """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # Single click
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()
                self.activateWindow()
    
    def closeEvent(self, event):
        """ Override close event to minimize to tray """
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Fluent QQ",
            "程序已最小化到系统托盘",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
