from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget, QSpacerItem, QSizePolicy, QStackedWidget
from qfluentwidgets import (SubtitleLabel, CaptionLabel, setFont, ScrollArea, TransparentPushButton,
                            FluentIcon as FIF, TabBar, TabCloseButtonDisplayMode, SegmentedWidget,
                            SimpleCardWidget, IconWidget, LineEdit, PrimaryPushButton)
from app.common.api_client import client
from app.view.components.image_widget import ImageWidget
from app.view.components.avatar_widget import AvatarWidget
from app.view.components.chat_bubble import ChatBubble
from app.common.time_utils import get_relative_time
from qfluentwidgets import (SubtitleLabel, CaptionLabel, setFont, ScrollArea, TransparentPushButton,
                            FluentIcon as FIF, TabBar, TabCloseButtonDisplayMode, SegmentedWidget,
                            SimpleCardWidget, IconWidget, LineEdit, PrimaryPushButton, qconfig, Theme, isDarkTheme)
import json

class MessageCard(SimpleCardWidget):
    """ Custom card to display message preview """
    openChatRequested = pyqtSignal(str, str, bool) # target_id, name, is_group

    def __init__(self, target_id, name, message, time_str, is_group=False, card_type="recent", parent=None):
        super().__init__(parent=parent)
        self.target_id = str(target_id)
        self.target_name = name
        self.is_group = is_group
        self.card_type = card_type # "recent", "friends", "groups"
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 12, 15, 12)
        self.layout.setSpacing(15)
        
        # Left: Avatar
        self.avatar_container = QWidget(self)
        self.avatar_container.setFixedSize(48, 48)
        self.avatar_container.setStyleSheet("background-color: transparent;")
        self.avatar_layout = QVBoxLayout(self.avatar_container)
        self.avatar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Avatar Widget
        if is_group:
            avatar_url = f"http://p.qlogo.cn/gh/{target_id}/{target_id}/100"
        else:
            avatar_url = f"http://q1.qlogo.cn/g?b=qq&nk={target_id}&s=640"
            
        self.avatar_icon = AvatarWidget(avatar_url, size=48, parent=self.avatar_container)
        self.avatar_layout.addWidget(self.avatar_icon, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Center: Name and Message
        self.text_container = QVBoxLayout()
        self.text_container.setSpacing(4)
        
        self.name_label = SubtitleLabel(name, self)
        setFont(self.name_label, 16, weight=600)
        
        if isinstance(message, list):
            display_msg = "".join([i.get("data", {}).get("text", "") for i in message if i.get("type") == "text"])
            if not display_msg: display_msg = "[非文本消息]"
        else:
            display_msg = str(message)
        
        self.msg_label = CaptionLabel(display_msg, self)
        self.msg_label.setWordWrap(False)
        
        self.text_container.addWidget(self.name_label)
        self.text_container.addWidget(self.msg_label)
        
        self.layout.addWidget(self.avatar_container)
        self.layout.addLayout(self.text_container)
        self.layout.addStretch(1)
        
        # Right: Time and Button
        self.right_container = QVBoxLayout()
        self.right_container.setSpacing(8)
        self.right_container.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.time_label = CaptionLabel(time_str, self)
        self.enter_btn = TransparentPushButton(FIF.CHEVRON_RIGHT, "", self)
        self.enter_btn.setFixedSize(32, 32)
        self.enter_btn.setIconSize(QSize(16, 16))
        self.enter_btn.clicked.connect(lambda: self.openChatRequested.emit(self.target_id, self.target_name, self.is_group))
        
        # Make whole card clickable
        self.clicked.connect(lambda: self.openChatRequested.emit(self.target_id, self.target_name, self.is_group))
        
        self.right_container.addWidget(self.time_label)
        self.right_container.addWidget(self.enter_btn)
        self.layout.addLayout(self.right_container)
        self.setFixedHeight(80)
        
        self._update_style()
        qconfig.themeChanged.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme):
        self._update_style(theme)

    def _update_style(self, theme=None):
        if theme is None:
            theme = qconfig.theme
        
        is_dark = theme == Theme.DARK or (theme == Theme.AUTO and isDarkTheme())
        
        if is_dark:
            self.msg_label.setStyleSheet("color: rgba(255, 255, 255, 0.6);")
        else:
            self.msg_label.setStyleSheet("color: rgba(0, 0, 0, 0.6);")

class ChatView(QWidget):
    """ Individual Chat View """
    def __init__(self, target_id, name, is_group=False, parent=None):
        super().__init__(parent=parent)
        self.target_id = target_id
        self.is_group = is_group
        self.chat_name = name
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 10, 20, 20)
        
        # Header
        self.header = QHBoxLayout()
        self.title_label = SubtitleLabel(name, self)
        setFont(self.title_label, 20, weight=600)
        self.header.addWidget(self.title_label)
        self.header.addStretch(1)
        
        # Message History
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        
        # Input Area
        self.input_area_widget = QWidget()
        self.input_area_layout = QHBoxLayout(self.input_area_widget)
        self.input_area_layout.setContentsMargins(0, 10, 0, 0)
        self.input_area_layout.setSpacing(10)
        
        self.upload_btn = TransparentPushButton(FIF.ADD, "", self)
        self.upload_btn.setFixedSize(32, 32)
        
        self.input_edit = LineEdit(self)
        self.input_edit.setPlaceholderText("在此输入消息...")
        self.input_edit.returnPressed.connect(self.sendMessage)
        
        self.send_btn = PrimaryPushButton("发送", self)
        self.send_btn.clicked.connect(self.sendMessage)
        
        self.input_area_layout.addWidget(self.upload_btn)
        self.input_area_layout.addWidget(self.input_edit, 1)
        self.input_area_layout.addWidget(self.send_btn)
        
        self.layout.addLayout(self.header)
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.input_area_widget)
        
        # Load History
        QTimer.singleShot(100, self.loadHistory)
        
        self.message_widgets = {} # message_id -> row_widget

    def onRecallRequested(self, message_id):
        """ Handle message recall """
        print(f"[ChatView] Recalling message: {message_id}")
        res = client.delete_msg(message_id)
        if res and res.get("status") == "ok":
            # Remove from UI
            if message_id in self.message_widgets:
                widget = self.message_widgets.pop(message_id)
                self.scroll_layout.removeWidget(widget)
                widget.deleteLater()
                print(f"[ChatView] Message {message_id} removed from UI")
        else:
            print(f"[ChatView] Failed to recall message {message_id}")
            from qfluentwidgets import InfoBar, InfoBarPosition
            InfoBar.error(
                title='撤回失败',
                content='无法撤回该消息，可能已超过时限。',
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

    def onReactRequested(self, message_id, emoji_id):
        """ Handle emoji reaction """
        print(f"[ChatView] Reacting to message: {message_id} with {emoji_id}")
        res = client.set_msg_emoji_like(message_id, emoji_id)
        if res and res.get("status") == "ok":
            from qfluentwidgets import InfoBar, InfoBarPosition
            InfoBar.success(
                title='回应成功',
                content='已发送表情回应',
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
        else:
            from qfluentwidgets import InfoBar, InfoBarPosition
            InfoBar.error(
                title='回应失败',
                content='无法发送表情回应',
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

    def loadHistory(self):
        """ Fetch and display recent chat history from NapCat """
        if not self.target_id or str(self.target_id).lower() == 'none':
            print(f"[UI] Invalid target_id for history loading: {self.target_id}")
            return
            
        res = client.get_history(self.target_id, self.is_group, count=20)
        if not res or res.get("status") != "ok":
            print(f"[UI] Failed to load history for {self.target_id}")
            return
            
        messages = res.get("data", {}).get("messages", [])
        for i, msg in enumerate(messages):
            sender = msg.get("sender", {})
            sender_name = sender.get("nickname", "用户")
            sender_id = sender.get("user_id")
            content = msg.get("message", "")
            time_val = msg.get("time")
            time_str = get_relative_time(time_val)
            msg_id = str(msg.get("message_id")) if msg.get("message_id") else None
            
            # Handle emoji likes
            emoji_likes = msg.get("emoji_likes_list", [])
            normalized_likes = []
            if emoji_likes:
                try:
                    # Check format
                    if isinstance(emoji_likes[0], dict):
                        if "count" in emoji_likes[0]:
                            normalized_likes = emoji_likes
                        elif "emoji_id" in emoji_likes[0]:
                            # Aggregate
                            counts = {}
                            for item in emoji_likes:
                                eid = str(item.get("emoji_id"))
                                counts[eid] = counts.get(eid, 0) + 1
                            normalized_likes = [{"emoji_id": eid, "count": c} for eid, c in counts.items()]
                except Exception as e:
                    print(f"[UI] Error processing emoji likes: {e}")

            # PROBE: Print message structure to check for emoji likes
            # if i == 0:
            #     print(f"[PROBE] Message Structure: {json.dumps(msg, indent=2, ensure_ascii=False)}")
            
            avatar_url = f"http://q1.qlogo.cn/g?b=qq&nk={sender_id}&s=640" if sender_id else None
            # Identification of self can be improved if we have current login ID
            self.addMessage(sender_name, content, is_self=False, avatar_url=avatar_url, message_id=msg_id, time_str=time_str, emoji_likes=normalized_likes)

    def addMessage(self, name, message, is_self=False, avatar_url=None, message_id=None, time_str="", emoji_likes=None):
        """ Add a message to the chat view """
        # Main container for the message row
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 8, 0, 8)
        row_layout.setSpacing(12)
        
        # Avatar
        if avatar_url:
            avatar = AvatarWidget(avatar_url, size=36, parent=row_widget)
        else:
            avatar = IconWidget(FIF.PEOPLE, row_widget)
            avatar.setFixedSize(36, 36)
        
        # Content container (Name + Bubble)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Name & Time Container
        name_container = QWidget()
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(8)
        
        if is_self:
             name_layout.addStretch(1)
             if time_str:
                 time_label = CaptionLabel(time_str, name_container)
                 time_label.setStyleSheet("color: #999999;")
                 name_layout.addWidget(time_label)
             name_label = CaptionLabel(name, name_container)
             name_layout.addWidget(name_label)
        else:
             name_label = CaptionLabel(name, name_container)
             name_layout.addWidget(name_label)
             if time_str:
                 time_label = CaptionLabel(time_str, name_container)
                 time_label.setStyleSheet("color: #999999;")
                 name_layout.addWidget(time_label)
             name_layout.addStretch(1)
        
        # Bubble Container
        bubble = ChatBubble(is_self, message_id, row_widget)
        if message_id:
            bubble.recallRequested.connect(self.onRecallRequested)
            bubble.reactRequested.connect(self.onReactRequested)
            # Store widget for recall
            self.message_widgets[str(message_id)] = row_widget

        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(12, 10, 12, 10)

        # Message Content Processing
        has_content = False
        if isinstance(message, list):
            for segment in message:
                seg_type = segment.get("type")
                seg_data = segment.get("data", {})
                
                if seg_type == "text":
                    text = seg_data.get("text", "")
                    if text:
                        msg_label = SubtitleLabel(text, bubble)
                        setFont(msg_label, 14)
                        msg_label.setWordWrap(True)
                        # Text color handled by parent bubble stylesheet
                        bubble_layout.addWidget(msg_label)
                        has_content = True
                        
                elif seg_type == "image":
                    image_url = seg_data.get("url") or seg_data.get("file")
                    if image_url:
                        try:
                            image_widget = ImageWidget(image_url, bubble)
                            # Limit max width of images in bubble
                            image_widget.setMaximumWidth(300)
                            bubble_layout.addWidget(image_widget)
                            has_content = True
                        except Exception as e:
                            print(f"[ChatView] Failed to create image widget: {e}")
                            error_label = CaptionLabel("[图片加载失败]", bubble)
                            bubble_layout.addWidget(error_label)
                            has_content = True
            
            if not has_content:
                msg_label = SubtitleLabel("[非文本消息]", bubble)
                setFont(msg_label, 14)
                bubble_layout.addWidget(msg_label)
        else:
            # Simple text message
            display_text = str(message)
            msg_label = SubtitleLabel(display_text, bubble)
            setFont(msg_label, 14)
            msg_label.setWordWrap(True)
            bubble_layout.addWidget(msg_label)
        
        if emoji_likes:
            bubble.setReactions(emoji_likes)

        # Layout Assembly
        if is_self:
            # Structure: [Stretch] [Content(Name+Bubble)] [Avatar]
            row_layout.addStretch(1)
            
            content_layout.addWidget(name_container, 0, Qt.AlignmentFlag.AlignRight)
            content_layout.addWidget(bubble, 0, Qt.AlignmentFlag.AlignRight)
            
            row_layout.addLayout(content_layout)
            row_layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignTop)
        else:
            # Structure: [Avatar] [Content(Name+Bubble)] [Stretch]
            row_layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignTop)
            
            content_layout.addWidget(name_container, 0, Qt.AlignmentFlag.AlignLeft)
            content_layout.addWidget(bubble, 0, Qt.AlignmentFlag.AlignLeft)
            
            row_layout.addLayout(content_layout)
            row_layout.addStretch(1)
            
        self.scroll_layout.addWidget(row_widget)
        
        # Scroll to bottom
        QTimer.singleShot(10, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def sendMessage(self):
        msg = self.input_edit.text().strip()
        if not msg: return
        
        res = client.send_message(self.target_id, msg, self.is_group)
        if res and res.get("status") == "ok":
            message_id = str(res.get("data", {}).get("message_id"))
            self.addMessage("我", msg, is_self=True, message_id=message_id, time_str="刚刚")
            self.input_edit.clear()
        else:
            self.addMessage("系统", "消息发送失败，请检查连接", is_self=False, time_str="刚刚")

class ChatInterface(QFrame):
    """ Main Chat Interface with TabBar and Multi-page Stack """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # 0. Top Navigation TabBar
        self.top_tab_bar = TabBar(self)
        self.top_tab_bar.setMovable(True)
        self.top_tab_bar.setScrollable(True)
        self.top_tab_bar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.ALWAYS)
        
        self.top_tab_bar.addTab("msg_center", "消息中心", FIF.MESSAGE)
        self.top_tab_bar.setAddButtonVisible(True)
        
        self.top_tab_bar.currentChanged.connect(self.onTabChanged)
        self.top_tab_bar.tabCloseRequested.connect(self.onTabClose)
        self.top_tab_bar.tabAddRequested.connect(self.goHome)
        self.top_tab_bar.tabBarClicked.connect(self.onTabBarClicked)
        
        # 1. Main Stack
        self.stacked_widget = QStackedWidget(self)
        
        # --- Page: Message Center ---
        self.msg_center_page = QWidget()
        self.msg_center_layout = QVBoxLayout(self.msg_center_page)
        self.msg_center_layout.setContentsMargins(0, 0, 0, 0)
        
        self.header = QWidget()
        self.header_layout = QVBoxLayout(self.header)
        self.header_layout.setContentsMargins(36, 20, 36, 12)
        self.title_label = SubtitleLabel("消息中心", self)
        setFont(self.title_label, 28, weight=600)
        self.status_label = CaptionLabel("正在连接服务器...", self)
        
        self.tab_bar = SegmentedWidget(self)
        self.tab_bar.addItem("recent", "最近消息")
        self.tab_bar.addItem("friends", "好友列表")
        self.tab_bar.addItem("groups", "群组列表")
        self.tab_bar.setCurrentItem("recent")
        self.tab_bar.currentItemChanged.connect(self.onSegmentedChanged)
        
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addWidget(self.status_label)
        self.header_layout.addWidget(self.tab_bar)
        
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(30, 10, 30, 30)
        self.scroll_layout.setSpacing(12)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        
        self.msg_center_layout.addWidget(self.header)
        self.msg_center_layout.addWidget(self.scroll_area)
        
        self.stacked_widget.addWidget(self.msg_center_page)
        self.layout.addWidget(self.top_tab_bar)
        self.layout.addWidget(self.stacked_widget)
        
        # State
        self.cards = {}
        self.chats = {} # routeKey -> ChatView instance
        self.friend_list = {} # ID -> Name
        self.group_list = {} # ID -> Name
        self.contact_map = {} # ID -> Name (full cache)
        
        self.setObjectName("chatInterface")
        
        # Load Data
        QTimer.singleShot(500, self.loadInitialData)

    def loadInitialData(self):
        """ Startup data loading """
        # Groups
        res = client.get_group_list()
        if res and res.get("status") == "ok":
            for g in res.get("data", []):
                gid = str(g["group_id"])
                name = g.get("group_name", f"群 {gid}")
                self.group_list[gid] = name
                self.contact_map[gid] = name
        
        # Friends
        res = client.get_friend_list()
        if res and res.get("status") == "ok":
            for f in res.get("data", []):
                uid = str(f["user_id"])
                name = f.get("nickname", f"用户 {uid}")
                self.friend_list[uid] = name
                self.contact_map[uid] = name
        
        print(f"[UI] Loaded {len(self.friend_list)} friends and {len(self.group_list)} groups")
        
        # Recent Messages
        res = client.get_recent_contact()
        if res and res.get("status") == "ok":
            for c in res.get("data", []):
                is_group = c.get("type") == "group"
                raw_id = c.get("group_id") if is_group else c.get("user_id")
                if raw_id is None: continue
                
                target_id = str(raw_id)
                name = self.contact_map.get(target_id, target_id)
                last_msg = c.get("last_msg", {}).get("text", "[无消息]")
                self._update_or_create_card(target_id, name, last_msg, "历史", is_group, "recent")
        
        # Populate Friends Tab
        for tid, name in self.friend_list.items():
            self._update_or_create_card(tid, name, "[点击开始聊天]", "", False, "friends")
            
        # Populate Groups Tab
        for tid, name in self.group_list.items():
            self._update_or_create_card(tid, name, "[点击查看群聊]", "", True, "groups")

        # Initial view: only "recent" visible
        self.onSegmentedChanged("recent")

    def onSegmentedChanged(self, key):
        """ Filter cards based on selected tab """
        print(f"[UI] Switching list to: {key}")
        for card_key, card in self.cards.items():
            # card_key is "type:id"
            ctype, _ = card_key.split(":", 1)
            card.setVisible(ctype == key)

    def goHome(self):
        self.top_tab_bar.setCurrentTab("msg_center")
        self.stacked_widget.setCurrentWidget(self.msg_center_page)

    def onTabBarClicked(self, index):
        # Explicit check if home tab clicked
        if index == 0:
            self.goHome()

    def onTabChanged(self, index_or_key):
        current_tab = self.top_tab_bar.currentTab()
        # Extract routeKey from TabItem object
        if hasattr(current_tab, 'routeKey'):
            routeKey = current_tab.routeKey()
        else:
            routeKey = str(current_tab)
        
        print(f"[UI] Tab changed to: {routeKey}")
        
        if routeKey == "msg_center":
            self.stacked_widget.setCurrentWidget(self.msg_center_page)
            print(f"[UI] Switched to message center")
        elif routeKey in self.chats:
            self.stacked_widget.setCurrentWidget(self.chats[routeKey])
            print(f"[UI] Switched to chat: {routeKey}")
        else:
            print(f"[UI] Warning: Unknown route key: {routeKey}")

    def onTabClose(self, index_or_key):
        print(f"[UI] Tab close requested for: {index_or_key} (type: {type(index_or_key)})")
        
        # If it's an integer, it's the tab index - we need to get the routeKey
        if isinstance(index_or_key, int):
            tab_index = index_or_key
            tab_item = self.top_tab_bar.tabItem(tab_index)
            if tab_item and hasattr(tab_item, 'routeKey'):
                routeKey = tab_item.routeKey()
            else:
                print(f"[UI] Warning: Could not get routeKey from tab at index {tab_index}")
                return
        else:
            routeKey = index_or_key
            # Need to find the index for this routeKey
            tab_index = None
            for i in range(self.top_tab_bar.count()):
                item = self.top_tab_bar.tabItem(i)
                if item and hasattr(item, 'routeKey') and item.routeKey() == routeKey:
                    tab_index = i
                    break
        
        print(f"[UI] Resolved routeKey: {routeKey}")
        
        # if routeKey == "msg_center": 
        #     print("[UI] Cannot close message center tab")
        #     return
            
        if routeKey in self.chats:
            print(f"[UI] Closing chat: {routeKey}")
            view = self.chats.pop(routeKey)
            self.stacked_widget.removeWidget(view)
            view.deleteLater()
            
            # Remove tab by index if we have it, otherwise by routeKey
            if tab_index is not None:
                self.top_tab_bar.removeTab(tab_index)
            else:
                self.top_tab_bar.removeTab(routeKey)
            
            # Check if we need to go home
            current_tab = self.top_tab_bar.currentTab()
            if current_tab is None or (hasattr(current_tab, 'routeKey') and current_tab.routeKey() == ""):
                self.goHome()
        else:
            print(f"[UI] Warning: routeKey {routeKey} not found in chats")

    def openChat(self, target_id, name, is_group):
        routeKey = f"chat_{target_id}"
        if routeKey not in self.chats:
            # Resolve name if it looks like ID
            real_name = self.contact_map.get(target_id, name)
            view = ChatView(target_id, real_name, is_group, self)
            self.chats[routeKey] = view
            self.stacked_widget.addWidget(view)
            self.top_tab_bar.addTab(routeKey, real_name, FIF.PEOPLE if is_group else FIF.CHAT)
        
        self.top_tab_bar.setCurrentTab(routeKey)
        self.stacked_widget.setCurrentWidget(self.chats[routeKey])

    def setConnected(self, connected: bool):
        if connected:
            self.status_label.setText("已连接到 NapCat QQ")
            self.status_label.setStyleSheet("color: #28a745;")
        else:
            self.status_label.setText("连接已断开，正在尝试重连...")
            self.status_label.setStyleSheet("color: #dc3545;")

    def format_message(self, content):
        if isinstance(content, list):
            text = "".join([i.get("data", {}).get("text", "") for i in content if i.get("type") == "text"])
            return text if text else "[非文本消息]"
        return str(content)

    def addMessage(self, data: dict):
        post_type = data.get("post_type")
        if post_type != "message": return
        
        message_type = data.get("message_type")
        sender_name = data.get("sender", {}).get("nickname", "用户")
        is_group = message_type == "group"
        
        raw_id = data.get("group_id") if is_group else data.get("user_id")
        if raw_id is None: return
        
        target_id = str(raw_id)
        content = data.get("message", "")
        time_val = data.get("time")
        time_str = get_relative_time(time_val) if time_val else "刚刚"
        
        # Use Cache
        target_name = self.contact_map.get(target_id, sender_name if not is_group else f"群聊 {target_id}")
        display_text = self.format_message(content)
        
        self._update_or_create_card(target_id, target_name, display_text, time_str, is_group)
        
        routeKey = f"chat_{target_id}"
        if routeKey in self.chats:
            sender_id = data.get("sender", {}).get("user_id")
            avatar_url = f"http://q1.qlogo.cn/g?b=qq&nk={sender_id}&s=640" if sender_id else None
            msg_id = str(data.get("message_id")) if data.get("message_id") else None
            
            # Handle emoji likes for incoming message
            emoji_likes = data.get("emoji_likes_list", [])
            normalized_likes = []
            if emoji_likes:
                try:
                    if isinstance(emoji_likes[0], dict):
                        if "count" in emoji_likes[0]:
                            normalized_likes = emoji_likes
                        elif "emoji_id" in emoji_likes[0]:
                            counts = {}
                            for item in emoji_likes:
                                eid = str(item.get("emoji_id"))
                                counts[eid] = counts.get(eid, 0) + 1
                            normalized_likes = [{"emoji_id": eid, "count": c} for eid, c in counts.items()]
                except Exception:
                    pass

            self.chats[routeKey].addMessage(sender_name, content, avatar_url=avatar_url, message_id=msg_id, time_str=time_str, emoji_likes=normalized_likes)

    def _update_or_create_card(self, target_id, name, text, time_str, is_group, card_type="recent"):
        card_key = f"{card_type}:{target_id}"
        if card_key in self.cards:
            card = self.cards[card_key]
            summary = text[:50] + "..." if len(text) > 50 else text
            card.msg_label.setText(summary)
            if card_type == "recent":
                self.scroll_layout.removeWidget(card)
                self.scroll_layout.insertWidget(0, card)
        else:
            card = MessageCard(target_id, name, text, time_str, is_group, card_type, self.scroll_widget)
            card.openChatRequested.connect(self.openChat)
            self.cards[card_key] = card
            self.scroll_layout.addWidget(card)
