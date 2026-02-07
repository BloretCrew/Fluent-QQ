from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QVBoxLayout
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, ScrollArea, 
                            ExpandLayout, Theme, OptionsSettingCard, PushSettingCard,
                            InfoBar, InfoBarIcon, FluentIcon as FIF)
from ..common.config import config

class SettingInterface(ScrollArea):
    """ Setting interface """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QFrame(self)
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.setObjectName("settingInterface")
        self.scrollWidget.setObjectName("scrollWidget")
        

        # Appearance
        self.appearanceGroup = SettingCardGroup("外观", self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            config.themeMode, FIF.BRUSH, "应用主题", "调整外观",
            texts=["Light", "Dark", "Auto"], parent=self.appearanceGroup
        )
        self.appearanceGroup.addSettingCard(self.themeCard)

        # Connection
        self.connectionGroup = SettingCardGroup("连接 (NapCat QQ)", self.scrollWidget)
        self.testBtn = PushSettingCard("测试连接", FIF.LINK, "连接测试", "测试与 NapCat 的 API 连接", parent=self.connectionGroup)
        self.connectionGroup.addSettingCard(self.testBtn)

        self.expandLayout.addWidget(self.appearanceGroup)
        self.expandLayout.addWidget(self.connectionGroup)
        
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        
        # Connect signals
        self.themeCard.optionChanged.connect(lambda c: config.set("theme", c.text()))
