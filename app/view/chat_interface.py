from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget, QSpacerItem, QSizePolicy, QStackedWidget, QFileDialog, QApplication, QDialog, QLabel, QPushButton
from PyQt6.QtGui import QImage, QPixmap, QClipboard, QKeyEvent
from qfluentwidgets import (SubtitleLabel, CaptionLabel, setFont, ScrollArea, TransparentPushButton,
                            FluentIcon as FIF, TabBar, TabCloseButtonDisplayMode, SegmentedWidget,
                            SimpleCardWidget, IconWidget, LineEdit, PrimaryPushButton, qconfig, Theme, isDarkTheme,
                            RoundMenu, Action)
from app.common.api_client import client
from app.view.components.image_widget import ImageWidget
from app.view.components.avatar_widget import AvatarWidget
from app.view.components.chat_bubble import ChatBubble, ChatTextLabel
from app.common.time_utils import get_relative_time
from app.common.config import config, MessageLayout
from app.common.history_manager import history_manager
from app.view.components.member_select_dialog import MemberSelectDialog
from qfluentwidgets import (SubtitleLabel, CaptionLabel, setFont, ScrollArea, TransparentPushButton,
                            FluentIcon as FIF, TabBar, TabCloseButtonDisplayMode, SegmentedWidget,
                            SimpleCardWidget, IconWidget, LineEdit, PrimaryPushButton, qconfig, Theme, isDarkTheme)
import json
import time

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

class ChatLineEdit(LineEdit):
    """ LineEdit that handles image pasting """
    imagePasted = pyqtSignal(QImage)
    
    def keyPressEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_V:
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()
            if mime_data.hasImage():
                event.accept()
                self.imagePasted.emit(clipboard.image())
                return
        super().keyPressEvent(event)

class ImagePasteDialog(QDialog):
    """ Dialog to preview and confirm sending pasted image """
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.setWindowTitle("发送图片确认")
        self.setFixedSize(400, 350)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = SubtitleLabel("确认发送这张图片吗？", self)
        layout.addWidget(title_label, 0, Qt.AlignmentFlag.AlignHCenter)
        
        # Image Preview
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Scale pixmap
        pixmap = QPixmap.fromImage(image)
        if not pixmap.isNull():
            scaled = pixmap.scaled(360, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled)
            
        layout.addWidget(self.image_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("取消", self)
        self.cancel_btn.setFixedSize(100, 32)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.send_btn = PrimaryPushButton("发送", self)
        self.send_btn.setFixedSize(100, 32)
        self.send_btn.clicked.connect(self.accept)
        
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.send_btn)
        btn_layout.addStretch(1)
        
        layout.addLayout(btn_layout)
        
        # Apply theme
        if isDarkTheme():
            self.setStyleSheet("background-color: #2b2b2b; color: white;")
            self.image_label.setStyleSheet("background-color: #3b3b3b; border: 1px solid #4b4b4b; border-radius: 8px;")
            self.cancel_btn.setStyleSheet("background-color: #3b3b3b; color: white; border: 1px solid #4b4b4b; border-radius: 4px;")
        else:
            self.setStyleSheet("background-color: white; color: black;")
            self.image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #e0e0e0; border-radius: 8px;")
            self.cancel_btn.setStyleSheet("background-color: #f0f0f0; color: black; border: 1px solid #d0d0d0; border-radius: 4px;")

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
        
        # Input Area Container (Vertical: Reply Bar + Input Row)
        self.input_area_widget = QWidget()
        self.input_main_layout = QVBoxLayout(self.input_area_widget)
        self.input_main_layout.setContentsMargins(0, 0, 0, 0)
        self.input_main_layout.setSpacing(0)
        
        # Reply Bar
        self.reply_bar = QWidget()
        self.reply_bar.setFixedHeight(36)
        self.reply_bar.hide()
        self.reply_bar.setObjectName("replyBar")
        self.reply_bar.setStyleSheet("#replyBar { background-color: rgba(127, 127, 127, 0.1); border-radius: 6px; }")
        self.reply_layout = QHBoxLayout(self.reply_bar)
        self.reply_layout.setContentsMargins(10, 0, 10, 0)
        self.reply_layout.setSpacing(10)
        
        self.reply_label = CaptionLabel("回复: ", self.reply_bar)
        self.reply_close_btn = TransparentPushButton(FIF.CLOSE, "", self.reply_bar)
        self.reply_close_btn.setFixedSize(26, 26)
        self.reply_close_btn.setIconSize(QSize(12, 12))
        self.reply_close_btn.setToolTip("取消回复")
        self.reply_close_btn.clicked.connect(self.exitReplyMode)
        
        self.reply_layout.addWidget(self.reply_label)
        self.reply_layout.addStretch(1)
        self.reply_layout.addWidget(self.reply_close_btn)
        
        # Input Row
        self.input_row = QWidget()
        self.input_area_layout = QHBoxLayout(self.input_row)
        self.input_area_layout.setContentsMargins(0, 10, 0, 0)
        self.input_area_layout.setSpacing(10)
        
        self.upload_btn = TransparentPushButton(FIF.ADD, "", self)
        self.upload_btn.setFixedSize(32, 32)
        self.upload_btn.setIconSize(QSize(18, 18))
        self.upload_btn.setStyleSheet("QPushButton { padding: 0px; margin: 0px; border: none; }")
        self.upload_btn.clicked.connect(self.showUploadMenu)
        
        self.at_btn = TransparentPushButton(FIF.PEOPLE, "", self)
        self.at_btn.setFixedSize(32, 32)
        self.at_btn.setIconSize(QSize(18, 18))
        self.at_btn.setToolTip("提及(@)")
        self.at_btn.setStyleSheet("QPushButton { padding: 0px; margin: 0px; border: none; }")
        self.at_btn.clicked.connect(self.showAtMenu)
        
        self.input_edit = ChatLineEdit(self)
        self.input_edit.imagePasted.connect(self.onImagePasted)
        self.input_edit.setPlaceholderText("在此输入消息...")
        self.input_edit.returnPressed.connect(self.sendMessage)
        
        self.send_btn = PrimaryPushButton("发送", self)
        self.send_btn.clicked.connect(self.sendMessage)
        
        self.input_area_layout.addWidget(self.upload_btn)
        self.input_area_layout.addWidget(self.at_btn)
        self.input_area_layout.addWidget(self.input_edit, 1)
        self.input_area_layout.addWidget(self.send_btn)
        
        self.input_main_layout.addWidget(self.reply_bar)
        self.input_main_layout.addWidget(self.input_row)
        
        self.layout.addLayout(self.header)
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.input_area_widget)
        
        # Load History
        QTimer.singleShot(100, self.loadHistory)
        
        self.message_widgets = {} # message_id -> row_widget
        self.reply_data = None # Current reply target
        self.pending_at_users = []
        self.pending_at_all = False
        
        self.member_map = {} # cache for group members (user_id -> nickname)
        if self.is_group:
            QTimer.singleShot(500, self._update_group_members)

        # Merge Logic State
        self.last_msg_sender_id = None
        self.last_msg_timestamp = 0
        self.last_msg_is_self = None

        config.chatFontFamily.valueChanged.connect(self.updateChatFont)

    def _update_group_members(self):
        """ Fetch group members to populate nickname cache """
        if not self.is_group or not self.target_id: return
        
        def _on_members(data):
            if not data: return
            for m in data:
                uid = str(m.get("user_id"))
                nick = m.get("card") or m.get("nickname")
                if uid and nick:
                    self.member_map[uid] = nick
                    
        import threading
        def _fetch():
            res = client.get_group_member_list(self.target_id)
            if res and res.get("status") == "ok":
                # Signal back to UI thread if needed, but simple dict update is thread-safe enough for read-mostly
                # Ideally use signal, but for now direct update
                _on_members(res.get("data"))
                
        threading.Thread(target=_fetch, daemon=True).start()

    def updateChatFont(self, font_family):
        """ Update font for all messages """
        # We need to iterate over all bubbles and update their labels
        # This is expensive, but requested by user
        font_family = str(font_family)
        for widget in self.message_widgets.values():
            bubble = widget.findChild(ChatBubble)
            if bubble:
                # Recursive find QLabels inside bubble
                labels = bubble.findChildren(QLabel)
                for label in labels:
                    font = label.font()
                    font.setFamily(font_family)
                    label.setFont(font)
                    
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
        """ Fetch and display recent chat history """
        if not self.target_id or str(self.target_id).lower() == 'none':
            print(f"[UI] Invalid target_id for history loading: {self.target_id}")
            return

        # Get self_id for identification
        self.current_self_id = None
        try:
            chat_interface = self.window().findChild(QFrame, "chatInterface")
            if chat_interface and chat_interface.self_id:
                self.current_self_id = str(chat_interface.self_id)
        except Exception:
            pass

        # 1. Load from Local DB
        local_msgs = history_manager.get_messages(self.target_id, self.is_group, limit=20)
        if local_msgs:
            print(f"[UI] Loaded {len(local_msgs)} local messages for {self.target_id}")
            for msg in local_msgs:
                self._process_msg_data(msg)

        # 2. Load from API
        # Use QTimer to run this slightly later or in background to avoid blocking UI render of local msgs
        QTimer.singleShot(100, self._fetch_remote_history)

    def _fetch_remote_history(self):
        res = client.get_history(self.target_id, self.is_group, count=20)
        if not res or res.get("status") != "ok":
            print(f"[UI] Failed to load remote history for {self.target_id}")
            return
            
        messages = res.get("data", {}).get("messages", [])
        
        # Save to DB
        history_manager.save_messages(self.target_id, self.is_group, messages)
        
        # Add to UI
        for msg in messages:
            self._process_msg_data(msg)

    def _get_msg_summary(self, message_data):
        """ Extract text summary from message data """
        if isinstance(message_data, str):
            return message_data
        
        text = ""
        if isinstance(message_data, list):
            for seg in message_data:
                if seg.get("type") == "text":
                    text += seg.get("data", {}).get("text", "")
                elif seg.get("type") == "image":
                    text += "[图片]"
                elif seg.get("type") == "face":
                    text += "[表情]"
                elif seg.get("type") == "at":
                    qq = seg.get("data", {}).get("qq", "")
                    text += f"@{qq} "
                elif seg.get("type") == "reply":
                    text += "[回复]"
        return text

    def _process_msg_data(self, msg):
        """ Process message data and add to UI """
        msg_id = str(msg.get("message_id")) if msg.get("message_id") else None
        
        sender = msg.get("sender", {})
        sender_name = sender.get("nickname", "用户")
        sender_id = str(sender.get("user_id"))
        content = msg.get("message", "")
        time_val = msg.get("time")
        time_str = get_relative_time(time_val)
        
        # Identify self
        is_self = (sender_id == self.current_self_id) if self.current_self_id else False
        
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
        
        # Handle Reply
        reply_text = None
        reply_ref_id = None
        if isinstance(content, list):
            for seg in content:
                if seg.get("type") == "reply":
                    reply_ref_id = seg.get("data", {}).get("id")
                    if reply_ref_id:
                        # Try local
                        ref_msg = history_manager.get_message_by_id(reply_ref_id)
                        if not ref_msg:
                            # Try remote
                            try:
                                res = client.get_msg(reply_ref_id)
                                if res and res.get("status") == "ok":
                                    ref_msg = res.get("data")
                            except:
                                pass
                        
                        if ref_msg:
                            r_sender = ref_msg.get("sender", {}).get("nickname", "用户")
                            r_content = self._get_msg_summary(ref_msg.get("message", ""))
                            reply_text = f"{r_sender}: {r_content}"
                        else:
                            reply_text = "回复消息 [加载失败]"
                    break

        avatar_url = f"http://q1.qlogo.cn/g?b=qq&nk={sender_id}&s=640" if sender_id else None
        
        # Update or Add
        if msg_id and msg_id in self.message_widgets:
            self.updateMessage(msg_id, emoji_likes=normalized_likes)
        else:
            self.addMessage(sender_name, content, is_self=is_self, avatar_url=avatar_url, message_id=msg_id, time_str=time_str, emoji_likes=normalized_likes, reply_text=reply_text, reply_id=reply_ref_id, sender_id=sender_id, timestamp=time_val)

    def updateMessage(self, message_id, emoji_likes=None):
        """ Update existing message in UI """
        row_widget = self.message_widgets.get(str(message_id))
        if not row_widget: return
        
        # Find bubble
        bubble = row_widget.findChild(ChatBubble)
        if bubble:
            if emoji_likes is not None:
                bubble.setReactions(emoji_likes)

    def addMessage(self, name, message, is_self=False, avatar_url=None, message_id=None, time_str="", emoji_likes=None, reply_text=None, reply_id=None, sender_id=None, timestamp=None):
        """ Add a message to the chat view """
        # Determine if we should merge with previous message
        should_merge = False
        MERGE_TIME_WINDOW = 180 # 3 minutes
        
        current_time = timestamp if timestamp else time.time()
        
        # Only merge if we have a valid sender_id (to avoid merging system messages or unknown senders improperly)
        if (sender_id is not None and 
            self.last_msg_sender_id is not None and 
            sender_id == self.last_msg_sender_id and 
            is_self == self.last_msg_is_self and
            abs(current_time - self.last_msg_timestamp) < MERGE_TIME_WINDOW and
            not reply_text): # Don't merge if it's a reply
            should_merge = True
            
        # Update last message state
        self.last_msg_sender_id = sender_id
        self.last_msg_timestamp = current_time
        self.last_msg_is_self = is_self

        # Main container for the message row
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        
        if should_merge:
            row_layout.setContentsMargins(0, 2, 0, 2)
        else:
            row_layout.setContentsMargins(0, 8, 0, 8)
            
        row_layout.setSpacing(12)
        
        # Avatar
        if not should_merge:
            if avatar_url:
                avatar = AvatarWidget(avatar_url, size=36, parent=row_widget)
            else:
                avatar = IconWidget(FIF.PEOPLE, row_widget)
                avatar.setFixedSize(36, 36)
        else:
            # Placeholder for alignment
            avatar = QWidget(row_widget)
            avatar.setFixedSize(36, 36)
            avatar.setStyleSheet("background: transparent;")
        
        # Content container (Name + Bubble)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Name & Time Container (Only if not merged)
        name_container = None
        if not should_merge:
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
            bubble.replyRequested.connect(self.enterReplyMode)
            bubble.replyClicked.connect(self.scrollToMessage)
            # Store widget for recall
            self.message_widgets[str(message_id)] = row_widget

        bubble_layout = bubble.layout()
        if bubble_layout is None:
            bubble_layout = QVBoxLayout(bubble)
            
        bubble_layout.setContentsMargins(12, 10, 12, 10)

        # Message Content Processing
        has_content = False
        if isinstance(message, list):
            current_text_block = ""
            
            for segment in message:
                seg_type = segment.get("type")
                seg_data = segment.get("data", {})
                
                if seg_type == "text":
                    t = seg_data.get("text", "")
                    if t:
                        t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
                        current_text_block += t
                        has_content = True
                        
                elif seg_type == "at":
                    qq = seg_data.get("qq", "")
                    # Highlight style
                    if is_self:
                        style = "color: white; font-weight: bold;"
                    else:
                        color = "#4cc2ff" if isDarkTheme() else "#0078D4"
                        style = f"color: {color}; font-weight: bold;"
                    
                    if str(qq) == "all":
                        display_name = "全体成员"
                    else:
                        # Try member_map first
                        display_name = self.member_map.get(str(qq))
                        # Then try global contact map
                        if not display_name:
                            try:
                                chat_interface = self.window().findChild(QFrame, "chatInterface")
                                if chat_interface and hasattr(chat_interface, 'contact_map'):
                                    display_name = chat_interface.contact_map.get(str(qq))
                            except:
                                pass
                        # Fallback to QQ
                        if not display_name:
                            display_name = str(qq)

                    current_text_block += f'&nbsp;<span style="{style}">@{display_name}</span>&nbsp;'
                    has_content = True
                    
                elif seg_type == "face":
                    current_text_block += "[表情]"
                    has_content = True
                    
                elif seg_type == "image":
                    if current_text_block:
                        msg_label = ChatTextLabel(current_text_block, bubble)
                        msg_label.setTextFormat(Qt.TextFormat.RichText)
                        msg_label.setWordWrap(True)
                        msg_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
                        font = msg_label.font()
                        font.setPixelSize(14)
                        font.setFamily(config.chatFontFamily.value)
                        msg_label.setFont(font)
                        bubble_layout.addWidget(msg_label)
                        current_text_block = ""
                    
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
            
            if current_text_block:
                msg_label = ChatTextLabel(current_text_block, bubble)
                msg_label.setTextFormat(Qt.TextFormat.RichText)
                msg_label.setWordWrap(True)
                msg_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
                font = msg_label.font()
                font.setPixelSize(14)
                font.setFamily(config.chatFontFamily.value)
                msg_label.setFont(font)
                bubble_layout.addWidget(msg_label)
            
            if not has_content:
                msg_label = SubtitleLabel("[非文本消息]", bubble)
                font = msg_label.font()
                font.setPixelSize(14)
                font.setFamily(config.chatFontFamily.value)
                msg_label.setFont(font)
                bubble_layout.addWidget(msg_label)
        else:
            # Simple text message
            display_text = str(message)
            msg_label = SubtitleLabel(display_text, bubble)
            font = msg_label.font()
            font.setPixelSize(14)
            font.setFamily(config.chatFontFamily.value)
            msg_label.setFont(font)
            msg_label.setWordWrap(True)
            bubble_layout.addWidget(msg_label)
        
        if emoji_likes:
            bubble.setReactions(emoji_likes)

        if reply_text:
            bubble.setReply(reply_text, reply_id)

        # Layout Assembly
        # Check config
        layout_mode = config.messageLayout.value
        align_right = is_self and (layout_mode == MessageLayout.RIGHT_SELF)

        if align_right:
            # Structure: [Stretch] [Content(Name+Bubble)] [Avatar]
            row_layout.addStretch(1)
            
            if name_container:
                content_layout.addWidget(name_container, 0, Qt.AlignmentFlag.AlignRight)
            content_layout.addWidget(bubble, 0, Qt.AlignmentFlag.AlignRight)
            
            row_layout.addLayout(content_layout)
            row_layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignTop)
        else:
            # Structure: [Avatar] [Content(Name+Bubble)] [Stretch]
            row_layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignTop)
            
            if name_container:
                content_layout.addWidget(name_container, 0, Qt.AlignmentFlag.AlignLeft)
            content_layout.addWidget(bubble, 0, Qt.AlignmentFlag.AlignLeft)
            
            row_layout.addLayout(content_layout)
            row_layout.addStretch(1)
            
        self.scroll_layout.addWidget(row_widget)
        
        # Scroll to bottom
        QTimer.singleShot(10, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def scrollToMessage(self, message_id):
        """ Scroll to a specific message """
        if not message_id: return
        
        message_id = str(message_id)
        widget = self.message_widgets.get(message_id)
        
        if widget:
            self.scroll_area.ensureWidgetVisible(widget)
            # Optional: Add visual cue
        else:
            from qfluentwidgets import InfoBar
            InfoBar.warning(
                title='无法定位消息',
                content='该消息不在当前视图中。',
                parent=self,
                duration=2000
            )

    def showUploadMenu(self):
        """ Show upload menu for Image/File """
        menu = RoundMenu(parent=self)
        
        img_action = Action(FIF.PHOTO, "发送图片", self)
        img_action.triggered.connect(self._onSendImage)
        menu.addAction(img_action)
        
        file_action = Action(FIF.DOCUMENT, "发送文件", self)
        file_action.triggered.connect(self._onSendFile)
        menu.addAction(file_action)
        
        # Position menu above the button
        pos = self.upload_btn.mapToGlobal(self.upload_btn.rect().topLeft())
        pos.setY(pos.y() - menu.sizeHint().height() - 10)
        menu.exec(pos)

    def _get_self_avatar_url(self):
        """ Get self avatar URL """
        # Need to access ChatInterface parent to get self_id
        # Since ChatView is child of QStackedWidget which is child of ChatInterface
        # This is a bit hacky, better to pass self_info to ChatView
        try:
            chat_interface = self.window().findChild(QFrame, "chatInterface")
            if chat_interface and chat_interface.self_id:
                return f"http://q1.qlogo.cn/g?b=qq&nk={chat_interface.self_id}&s=640"
        except Exception:
            pass
        return None
        
    def _get_self_name(self):
        """ Get self nickname """
        try:
            chat_interface = self.window().findChild(QFrame, "chatInterface")
            if chat_interface and chat_interface.self_name:
                return chat_interface.self_name
        except Exception:
            pass
        return "我"

    def _onSendImage(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if not file_path:
            return
            
        res = client.send_image(self.target_id, file_path, self.is_group)
        if res and res.get("status") == "ok":
            message_id = str(res.get("data", {}).get("message_id"))
            # Construct local segment for display
            import os
            abs_path = os.path.abspath(file_path).replace("\\", "/")
            msg_data = [{"type": "image", "data": {"file": f"file:///{abs_path}"}}]
            
            self.addMessage(self._get_self_name(), msg_data, is_self=True, message_id=message_id, time_str="刚刚", avatar_url=self._get_self_avatar_url(), sender_id=self._get_self_id(), timestamp=time.time())
        else:
            from qfluentwidgets import InfoBar
            InfoBar.error(title='发送失败', content='图片发送失败', parent=self)

    def _onSendFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*.*)")
        if not file_path:
            return
            
        # Notify user uploading started
        from qfluentwidgets import InfoBar
        InfoBar.info(title='正在上传', content='文件上传中...', parent=self)
        
        res = client.upload_file(self.target_id, file_path, self.is_group)
        if res and res.get("status") == "ok":
            import os
            filename = os.path.basename(file_path)
            self.addMessage(self._get_self_name(), f"[文件] {filename} 已上传", is_self=True, time_str="刚刚", avatar_url=self._get_self_avatar_url(), sender_id=self._get_self_id(), timestamp=time.time())
            InfoBar.success(title='上传成功', content='文件已发送', parent=self)
        else:
            InfoBar.error(title='上传失败', content='文件上传失败', parent=self)

    def onImagePasted(self, image):
        """ Handle pasted image """
        dlg = ImagePasteDialog(image, self)
        if dlg.exec():
            # Save to temp file
            import tempfile
            import os
            
            # Create temp file
            fd, path = tempfile.mkstemp(suffix=".png")
            os.close(fd)
            
            try:
                if image.save(path, "PNG"):
                    # Send using existing send_image logic
                    res = client.send_image(self.target_id, path, self.is_group)
                    
                    if res and res.get("status") == "ok":
                        message_id = str(res.get("data", {}).get("message_id"))
                        # Construct local segment for display
                        abs_path = os.path.abspath(path).replace("\\", "/")
                        msg_data = [{"type": "image", "data": {"file": f"file:///{abs_path}"}}]
                        
                        self.addMessage(self._get_self_name(), msg_data, is_self=True, message_id=message_id, time_str="刚刚", avatar_url=self._get_self_avatar_url(), sender_id=self._get_self_id(), timestamp=time.time())
                    else:
                        from qfluentwidgets import InfoBar
                        InfoBar.error(title='发送失败', content='图片发送失败', parent=self)
                else:
                    print("[UI] Failed to save pasted image to temp file")
            except Exception as e:
                print(f"[UI] Error handling pasted image: {e}")

    def _get_self_id(self):
        try:
             chat_interface = self.window().findChild(QFrame, "chatInterface")
             if chat_interface and hasattr(chat_interface, 'self_id') and chat_interface.self_id:
                  return str(chat_interface.self_id)
        except:
             pass
        return "0"

    def _get_group_members(self):
        if not self.target_id: return []
        try:
            res = client.call_api("get_group_member_list", {"group_id": int(self.target_id)})
            if res and res.get("status") == "ok":
                return res.get("data", [])
        except Exception as e:
            print(f"Error fetching members: {e}")
        return []

    def showAtMenu(self):
        if not self.is_group:
             self.input_edit.setText(self.input_edit.text() + "@")
             self.input_edit.setFocus()
             return

        members = self._get_group_members()
        if not members:
            self.input_edit.setText(self.input_edit.text() + "@")
            self.input_edit.setFocus()
            return
            
        # Determine current user's role
        current_role = "member"
        self_id = self._get_self_id()
        for m in members:
            if str(m.get("user_id")) == str(self_id):
                current_role = m.get("role", "member")
                break
            
        dlg = MemberSelectDialog(members, current_role, self)
        if dlg.exec():
             selected = dlg.selected_members
             text = self.input_edit.text()
             if text and not text.endswith(" "):
                 text += " "
                 
             for m in selected:
                  if m.get('user_id') == 'all':
                       text += "@all "
                       self.pending_at_all = True
                  else:
                       name = m.get("card") or m.get("nickname") or str(m.get('user_id'))
                       text += f"@{name} "
                       self.pending_at_users.append(m)
             
             self.input_edit.setText(text)
             self.input_edit.setFocus()

    def enterReplyMode(self, message_id):
        """ Enter reply mode for a message """
        # Resolve message content
        reply_text = f"回复: [ID:{message_id}]"
        raw_text = ""
        
        # Try local first
        ref_msg = history_manager.get_message_by_id(message_id)
        if not ref_msg:
             # Try remote
             try:
                 res = client.get_msg(message_id)
                 if res and res.get("status") == "ok":
                     ref_msg = res.get("data")
             except:
                 pass
        
        if ref_msg:
            r_sender = ref_msg.get("sender", {}).get("nickname", "用户")
            raw_text = self._get_msg_summary(ref_msg.get("message", ""))
            # Limit length
            if len(raw_text) > 20: raw_text = raw_text[:20] + "..."
            reply_text = f"回复 {r_sender}: {raw_text}"
            
        self.reply_data = {"id": message_id, "text": f"{r_sender}: {raw_text}" if ref_msg else f"消息 {message_id}"}
        self.reply_bar.show()
        self.reply_label.setText(reply_text) 
        self.input_edit.setFocus()
        
    def exitReplyMode(self):
        """ Exit reply mode """
        self.reply_data = None
        self.reply_bar.hide()

    def sendMessage(self):
        msg = self.input_edit.text().strip()
        if not msg: return
        
        self.input_edit.clear()
        
        # Prepare content
        sent_content = []
        
        # 1. Handle Reply
        if self.reply_data:
            sent_content.append({"type": "reply", "data": {"id": self.reply_data["id"]}})

        # 2. Parse At segments
        import re
        entities = []
        
        # Check for @all
        if self.pending_at_all:
             for m in re.finditer(r"@all|@全体成员", msg):
                  entities.append({"start": m.start(), "end": m.end(), "type": "at", "data": {"qq": "all"}})
        
        # Check for individual users
        for u in self.pending_at_users:
             name = u.get("card") or u.get("nickname") or str(u.get("user_id"))
             escaped_name = re.escape(name)
             pattern = f"@{escaped_name}"
             for m in re.finditer(pattern, msg):
                  entities.append({"start": m.start(), "end": m.end(), "type": "at", "data": {"qq": u.get("user_id")}})

        # Sort and Filter overlaps
        entities.sort(key=lambda x: x["start"])
        clean_entities = []
        last_end = 0
        for e in entities:
             if e["start"] >= last_end:
                  clean_entities.append(e)
                  last_end = e["end"]
        
        # Construct segments
        segments = []
        last_idx = 0
        for e in clean_entities:
             if e["start"] > last_idx:
                  segments.append({"type": "text", "data": {"text": msg[last_idx:e["start"]]}})
             segments.append({"type": e["type"], "data": e["data"]})
             last_idx = e["end"]
        
        if last_idx < len(msg):
             segments.append({"type": "text", "data": {"text": msg[last_idx:]}})
             
        if not segments:
             segments.append({"type": "text", "data": {"text": msg}})
             
        sent_content.extend(segments)
        
        # Reset pending state
        self.pending_at_users = []
        self.pending_at_all = False
        
        # Send
        reply_display_text = self.reply_data.get("text") if self.reply_data else None
        
        res = client.send_message(self.target_id, sent_content, self.is_group)
        if self.reply_data:
             self.exitReplyMode()
             
        if res and res.get("status") == "ok":
            message_id = str(res.get("data", {}).get("message_id"))
            
            # Save to history
            try:
                msg_data = {
                    "message_id": message_id,
                    "message_type": "group" if self.is_group else "private",
                    "time": int(time.time()),
                    "sender": {
                        "user_id": self._get_self_id(),
                        "nickname": self._get_self_name()
                    },
                    "message": sent_content
                }
                history_manager.save_message(self.target_id, self.is_group, msg_data)
            except Exception as e:
                print(f"[UI] Error saving sent message: {e}")

            self.addMessage(self._get_self_name(), sent_content, is_self=True, message_id=message_id, time_str="刚刚", avatar_url=self._get_self_avatar_url(), reply_text=reply_display_text, sender_id=self._get_self_id(), timestamp=time.time())
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
        
        # Self Info
        self.self_id = None
        self.self_name = "我"
        
        self.setObjectName("chatInterface")
        
        # Load Data
        QTimer.singleShot(500, self.loadInitialData)
        
        # Listen for messages
        client.messageReceived.connect(self.addMessage)

    def loadInitialData(self):
        """ Startup data loading """
        # Login Info
        res = client.get_login_info()
        if res and res.get("status") == "ok":
            data = res.get("data", {})
            self.self_id = str(data.get("user_id"))
            self.self_name = data.get("nickname", "我")
            print(f"[UI] Logged in as: {self.self_name} ({self.self_id})")
        
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
            
            # Fetch Self Info
            try:
                res = client.call_api("get_login_info")
                if res and res.get("status") == "ok":
                    self.self_id = str(res.get("data", {}).get("user_id"))
                    history_manager.set_user_id(self.self_id)
                    print(f"[UI] Self ID: {self.self_id}")
            except Exception as e:
                print(f"[UI] Failed to get login info: {e}")
                
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
        
        # Save to history
        history_manager.save_message(target_id, is_group, data)
        
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

            self.chats[routeKey].addMessage(sender_name, content, avatar_url=avatar_url, message_id=msg_id, time_str=time_str, emoji_likes=normalized_likes, sender_id=sender_id, timestamp=time_val)

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
