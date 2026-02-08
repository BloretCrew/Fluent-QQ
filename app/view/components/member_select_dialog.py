
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem
from qfluentwidgets import SearchLineEdit, PrimaryPushButton, CheckBox, InfoBar, BodyLabel

class MemberSelectDialog(QDialog):
    """ Dialog to select group members """
    
    def __init__(self, members, current_role="member", parent=None):
        super().__init__(parent)
        self.members = members # list of {user_id, nickname, card, role}
        self.current_role = current_role
        self.selected_members = []
        self.is_at_all = False
        
        self.setWindowTitle("选择提醒的人")
        self.resize(400, 500)
        
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(20, 20, 20, 20)
        self.v_layout.setSpacing(12)
        
        # Search
        self.search_edit = SearchLineEdit(self)
        self.search_edit.setPlaceholderText("搜索群成员")
        self.search_edit.textChanged.connect(self.filter_members)
        self.v_layout.addWidget(self.search_edit)
        
        # List
        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.NoSelection) # Handle via checkbox
        self.v_layout.addWidget(self.list_widget)
        
        # Populate
        self.items = []
        for m in members:
            item = QListWidgetItem()
            name = m.get("card") or m.get("nickname") or str(m.get("user_id"))
            item.setText(name)
            item.setData(Qt.ItemDataRole.UserRole, m)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)
            self.items.append(item)
        
        # List item changed
        self.list_widget.itemChanged.connect(self.on_item_changed)

        # @All option (if admin)
        self.at_all_cb = None
        if current_role in ["owner", "admin"]:
            self.at_all_cb = CheckBox("全体成员 (@all)", self)
            self.at_all_cb.stateChanged.connect(self.on_at_all_changed)
            self.v_layout.addWidget(self.at_all_cb)
        
        # Count Label
        self.count_label = BodyLabel("已选择: 0", self)
        self.v_layout.addWidget(self.count_label)

        # Buttons
        btn_layout = QHBoxLayout()
        self.cancel_btn = PrimaryPushButton("取消", self)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.confirm_btn = PrimaryPushButton("确定", self)
        self.confirm_btn.clicked.connect(self.on_confirm)
        
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.confirm_btn)
        self.v_layout.addLayout(btn_layout)
        
    def filter_members(self, text):
        for item in self.items:
            data = item.data(Qt.ItemDataRole.UserRole)
            name = data.get("card") or data.get("nickname") or str(data.get("user_id"))
            item.setHidden(text.lower() not in name.lower())
            
    def on_at_all_changed(self, state):
        if state == Qt.CheckState.Checked.value: # Checked
             self.list_widget.setEnabled(False)
             self.is_at_all = True
             self.count_label.setText("已选择: 全体成员")
        else:
             self.list_widget.setEnabled(True)
             self.is_at_all = False
             self.update_count()

    def on_item_changed(self, item):
        self.update_count()
        
    def update_count(self):
        count = 0
        for item in self.items:
            if item.checkState() == Qt.CheckState.Checked:
                count += 1
        self.count_label.setText(f"已选择: {count}")

    def on_confirm(self):
        if self.is_at_all:
            self.selected_members = [{"user_id": "all", "nickname": "全体成员"}]
            self.accept()
            return

        # Check limit
        selected = []
        for item in self.items:
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.data(Qt.ItemDataRole.UserRole))
        
        if len(selected) > 20: # Limit
             InfoBar.warning("提示", "单次最多选择20人", parent=self)
             return
             
        self.selected_members = selected
        self.accept()
