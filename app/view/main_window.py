from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtGui import QIcon

from qfluentwidgets import (FluentWindow, NavigationItemPosition, FluentIcon as FIF, SplashScreen)

from app.view.chat_interface import ChatInterface
from app.view.contact_interface import ContactInterface
from app.view.setting_interface import SettingInterface
from app.common.config import config
from app.common.api_client import client
import app.common.notification_handler as notification_handler

try:
    from win11toast import toast
except ImportError:
    toast = None

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize UI
        self.initWindow()
        
        # Create sub interfaces
        self.chat_interface = ChatInterface(self)
        self.contact_interface = ContactInterface(self)
        self.setting_interface = SettingInterface(self)
        
        # Add sub interfaces
        self.initNavigation()
        
        # System Tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('qq.png'))
        self.tray_icon.activated.connect(self.onTrayIconActivated)
        self.tray_icon.show()
        
        # Listen for global messages
        client.messageReceived.connect(self.onMessageReceived)
        
        # Start WebSocket connection
        client.start_ws()
        
    def initNavigation(self):
        self.addSubInterface(self.chat_interface, FIF.CHAT, '聊天')
        self.addSubInterface(self.contact_interface, FIF.PEOPLE, '联系人')
        self.addSubInterface(self.setting_interface, FIF.SETTING, '设置', position=NavigationItemPosition.BOTTOM)
        
    def initWindow(self):
        self.resize(1000, 650)
        self.setWindowIcon(QIcon('qq.png'))
        self.setWindowTitle('Fluent QQ')
        
        # Center window
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        
    def onTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.showNormal()
            self.activateWindow()

    def closeEvent(self, event):
        """ Override close event to minimize to tray """
        if config.get("minimizeToTray", True):
             event.ignore()
             self.hide()
        else:
             super().closeEvent(event)
             
    def onMessageReceived(self, message):
        """ Handle global message notifications """
        if not config.get("enableWindowsNotification"):
            return
            
        if toast is None:
            return

        # Avoid notifying for self messages
        # Note: We don't have self_id easily available here without checking login info
        
        # Extract info
        msg_type = message.get("message_type")
        is_group = msg_type == "group"
        
        sender = message.get("sender", {})
        sender_name = sender.get("nickname", "Unknown")
        user_id = sender.get("user_id")
        
        if is_group:
            target_id = message.get("group_id")
            title = f"{sender_name} (群 {target_id})"
        else:
            target_id = user_id
            title = sender_name
            
        raw_msg = message.get("raw_message", "[收到新消息]")
        
        # Launch params for callback
        launch_params = f"target_id={target_id}&is_group={is_group}"
        
        try:
            # Note: on_click will run in a separate process/thread
            toast(
                title,
                raw_msg,
                input='回复',
                button='发送',
                on_click=notification_handler.handle_reply,
                launch=launch_params
            )
        except Exception as e:
            print(f"[UI] Toast Error: {e}")
