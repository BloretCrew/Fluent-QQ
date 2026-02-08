from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget
from qfluentwidgets import (SubtitleLabel, CaptionLabel, setFont, ScrollArea, TransparentPushButton,
                            FluentIcon as FIF, SegmentedWidget, SimpleCardWidget, IconWidget, SearchLineEdit,
                            qconfig, Theme, isDarkTheme)
from app.common.api_client import client

class ContactCard(SimpleCardWidget):
    """ Contact card for displaying friend or group """
    openChatRequested = pyqtSignal(str, str, bool)  # target_id, name, is_group

    def __init__(self, target_id, name, is_group=False, parent=None):
        super().__init__(parent=parent)
        self.target_id = str(target_id)
        self.target_name = name
        self.is_group = is_group
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 12, 15, 12)
        self.layout.setSpacing(15)
        
        # Left: Avatar
        self.avatar_container = QWidget(self)
        self.avatar_container.setFixedSize(48, 48)
        self.avatar_layout = QVBoxLayout(self.avatar_container)
        self.avatar_layout.setContentsMargins(0, 0, 0, 0)
        
        icon = FIF.PEOPLE if is_group else FIF.CHAT
        self.avatar_icon = IconWidget(icon, self.avatar_container)
        self.avatar_icon.setFixedSize(24, 24)
        self.avatar_layout.addWidget(self.avatar_icon, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Center: Name
        self.name_label = SubtitleLabel(name, self)
        setFont(self.name_label, 16, weight=600)
        
        # Right: Enter button
        self.enter_btn = TransparentPushButton(FIF.CHEVRON_RIGHT, "", self)
        self.enter_btn.setFixedSize(32, 32)
        self.enter_btn.setIconSize(QSize(16, 16))
        self.enter_btn.clicked.connect(lambda: self.openChatRequested.emit(self.target_id, self.target_name, self.is_group))
        
        # Make whole card clickable
        self.clicked.connect(lambda: self.openChatRequested.emit(self.target_id, self.target_name, self.is_group))
        
        self.layout.addWidget(self.avatar_container)
        self.layout.addWidget(self.name_label)
        self.layout.addStretch(1)
        self.layout.addWidget(self.enter_btn)
        self.setFixedHeight(72)
        
        self._update_style()
        qconfig.themeChanged.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme):
        self._update_style(theme)

    def _update_style(self, theme=None):
        if theme is None:
            theme = qconfig.theme
        
        is_dark = theme == Theme.DARK or (theme == Theme.AUTO and isDarkTheme())
        
        if is_dark:
            self.avatar_container.setStyleSheet("background-color: #333333; border-radius: 24px;")
        else:
            self.avatar_container.setStyleSheet("background-color: #f0f0f0; border-radius: 24px;")

class ContactInterface(QFrame):
    """ Contact interface with friends and groups """
    openChatRequested = pyqtSignal(str, str, bool)  # Forward signal to main window
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Header
        self.header = QWidget()
        self.header_layout = QVBoxLayout(self.header)
        self.header_layout.setContentsMargins(36, 20, 36, 12)
        
        self.title_label = SubtitleLabel("联系人", self)
        setFont(self.title_label, 28, weight=600)
        
        # Search box
        self.search_box = SearchLineEdit(self)
        self.search_box.setPlaceholderText("搜索联系人...")
        self.search_box.textChanged.connect(self.onSearchTextChanged)
        self.search_box.setFixedWidth(400)
        
        # Tab bar
        self.tab_bar = SegmentedWidget(self)
        self.tab_bar.addItem("friends", "好友")
        self.tab_bar.addItem("groups", "群组")
        self.tab_bar.setCurrentItem("friends")
        self.tab_bar.currentItemChanged.connect(self.onTabChanged)
        
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addWidget(self.search_box)
        self.header_layout.addWidget(self.tab_bar)
        
        # Scroll area for contacts
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(30, 10, 30, 30)
        self.scroll_layout.setSpacing(12)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.scroll_area)
        
        self.setObjectName("contactInterface")
        
        # State
        self.friend_cards = {}  # id -> ContactCard
        self.group_cards = {}   # id -> ContactCard
        self.friend_list = {}   # id -> name
        self.group_list = {}    # id -> name
        
        # Load data
        QTimer.singleShot(500, self.loadContacts)
    
    def loadContacts(self):
        """ Load friends and groups from API """
        # Load groups
        res = client.get_group_list()
        if res and res.get("status") == "ok":
            for g in res.get("data", []):
                gid = str(g["group_id"])
                name = g.get("group_name", f"群 {gid}")
                self.group_list[gid] = name
                
                card = ContactCard(gid, name, is_group=True, parent=self.scroll_widget)
                card.openChatRequested.connect(self.openChatRequested.emit)
                self.group_cards[gid] = card
                self.scroll_layout.addWidget(card)
                card.hide()  # Initially hidden
        
        # Load friends
        res = client.get_friend_list()
        if res and res.get("status") == "ok":
            for f in res.get("data", []):
                uid = str(f["user_id"])
                name = f.get("nickname", f"用户 {uid}")
                self.friend_list[uid] = name
                
                card = ContactCard(uid, name, is_group=False, parent=self.scroll_widget)
                card.openChatRequested.connect(self.openChatRequested.emit)
                self.friend_cards[uid] = card
                self.scroll_layout.addWidget(card)
        
        print(f"[ContactInterface] Loaded {len(self.friend_list)} friends and {len(self.group_list)} groups")
        
        # Show initial tab
        self.onTabChanged("friends")
    
    def onTabChanged(self, key):
        """ Switch between friends and groups """
        for card in self.friend_cards.values():
            card.setVisible(key == "friends")
        for card in self.group_cards.values():
            card.setVisible(key == "groups")
    
    def onSearchTextChanged(self, text):
        """ Filter contacts based on search text """
        text = text.lower().strip()
        current_tab = self.tab_bar.currentItem()
        
        if current_tab == "friends":
            for uid, card in self.friend_cards.items():
                name = self.friend_list.get(uid, "").lower()
                card.setVisible(text in name or text in uid)
        else:
            for gid, card in self.group_cards.items():
                name = self.group_list.get(gid, "").lower()
                card.setVisible(text in name or text in gid)
