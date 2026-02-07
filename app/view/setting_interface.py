from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QVBoxLayout
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, ScrollArea, 
                            ExpandLayout, Theme, OptionsSettingCard, PushSettingCard,
                            InfoBar, InfoBarIcon, FluentIcon as FIF)
from ..common.config import config, ImagePreviewMode

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
            config.themeMode, FIF.BRUSH, "应用主题", "调整外观（重启生效）",
            texts=["Light", "Dark", "Auto"], parent=self.appearanceGroup
        )
        self.appearanceGroup.addSettingCard(self.themeCard)

        # Behavior
        self.behaviorGroup = SettingCardGroup("行为", self.scrollWidget)
        self.imagePreviewCard = OptionsSettingCard(
            config.imagePreviewMode, FIF.PHOTO, "图片预览方式", "选择点击图片时的打开方式",
            texts=["QuickLook", "系统默认打开"], parent=self.behaviorGroup
        )
        self.behaviorGroup.addSettingCard(self.imagePreviewCard)

        # Connection
        self.connectionGroup = SettingCardGroup("连接 (NapCat QQ)", self.scrollWidget)
        self.testBtn = PushSettingCard("测试连接", FIF.LINK, "连接测试", "测试与 NapCat 的 API 连接", parent=self.connectionGroup)
        self.connectionGroup.addSettingCard(self.testBtn)

        self.expandLayout.addWidget(self.appearanceGroup)
        self.expandLayout.addWidget(self.behaviorGroup)
        self.expandLayout.addWidget(self.connectionGroup)
        
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setStyleSheet("ScrollArea { background: transparent; border: none; }")
        
        # Connect signals
        # self.themeCard.optionChanged.connect(lambda c: config.set("theme", c.value))
        # self.imagePreviewCard.optionChanged.connect(lambda c: config.set("imagePreviewMode", c.value))
