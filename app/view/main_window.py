from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from qfluentwidgets import (FluentWindow, NavigationItemPosition, FluentIcon as FIF,
                            setTheme, Theme, setThemeColor)
from qfluentwidgets import FluentIcon as FIF

from .chat_interface import ChatInterface
from .contact_interface import ContactInterface
from .setting_interface import SettingInterface
from ..common.config import config
from ..common.api_client import client

class MainWindow(FluentWindow):
    """ Main window """
    def __init__(self):
        super().__init__()
        
        # Create sub interfaces
        self.chatInterface = ChatInterface(self)
        self.contactInterface = ContactInterface(self)
        self.settingInterface = SettingInterface(self)
        
        self.initNavigation()
        self.initWindow()

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
        
        # Apply theme
        self.applyTheme(config.get("theme"))
        config.themeChanged.connect(self.applyTheme)

    def applyTheme(self, theme):
        setTheme(theme)
