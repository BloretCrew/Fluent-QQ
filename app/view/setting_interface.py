from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QVBoxLayout
from PyQt6.QtGui import QFontDatabase
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, ScrollArea, 
                            ExpandLayout, Theme, OptionsSettingCard, PushSettingCard,
                            ComboBoxSettingCard, InfoBar, InfoBarIcon, FluentIcon as FIF)
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
        self.messageLayoutCard = OptionsSettingCard(
            config.messageLayout, FIF.ALIGNMENT, "消息显示方式", "选择聊天气泡的排列方式",
            texts=["Right Self", "All Left"], parent=self.appearanceGroup
        )
        
        # Chat Font
        self.fontCard = ComboBoxSettingCard(
            config.chatFontFamily, FIF.FONT_SIZE, "聊天字体", "设置全局聊天区域的字体",
            texts=[], parent=self.appearanceGroup
        )
        
        # Populate fonts
        available_fonts = QFontDatabase.families()
        priority_fonts = ["Microsoft YaHei", "SimSun", "Segoe UI", "Arial", "Times New Roman"]
        sorted_fonts = []
        
        # Add priority fonts first if they exist
        for f in priority_fonts:
            if f in available_fonts:
                sorted_fonts.append(f)
                
        # Add remaining
        for f in available_fonts:
            if f not in sorted_fonts:
                sorted_fonts.append(f)
                
        self.fontCard.addItems(sorted_fonts)
        self.fontCard.setValue(config.chatFontFamily.value)
        
        self.appearanceGroup.addSettingCard(self.themeCard)
        self.appearanceGroup.addSettingCard(self.messageLayoutCard)
        self.appearanceGroup.addSettingCard(self.fontCard)

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
