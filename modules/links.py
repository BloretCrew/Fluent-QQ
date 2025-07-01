from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
# 以下导入的部分是 Fluent QQ 所有 © 2025 Fluent QQ All rights reserved. © 2025 Bloret All rights reserved.的模块，位于 modules 中
from modules.log import log, importlog

def open_github_bloret_Launcher():
    QDesktopServices.openUrl(QUrl("https://github.com/BloretCrew/Fluent-QQ"))
    log("打开该项目的 Github 页面")
def open_qq_link():
    QDesktopServices.openUrl(QUrl("https://qm.qq.com/q/iGw0GwUCiI"))
    log("打开 Bloret QQ 群页面")
def open_BLC_qq_link():
    QDesktopServices.openUrl(QUrl("https://qm.qq.com/q/kEt8fb41wc"))
    log("打开 BLC QQ 群页面")
def open_BBBS_link(server_ip):
    QDesktopServices.openUrl(QUrl(server_ip+"bbs/"))
    log("打开 BBBS 页面")
def open_BBBS_Reg_link(server_ip):
    QDesktopServices.openUrl(QUrl(server_ip+"bbs/reg/"))
    log("打开 BBBS 注册页面")
def open_bloret_web():
    QDesktopServices.openUrl(QUrl("http://pcfs.top:2"))
    log("打开 Fluent QQ 网页")
def open_github_bloret():
    QDesktopServices.openUrl(QUrl("https://github.com/BloretCrew"))
    log("打开 Bloret Github 组织页面")
def copy_skin_to_clipboard(self):
    clipboard = QApplication.clipboard()
    clipboard.setText(self.player_skin)
    log(f"皮肤URL {self.player_skin} 已复制到剪贴板")
def copy_cape_to_clipboard(self):
    clipboard = QApplication.clipboard()
    clipboard.setText(self.player_cape)
    log(f"披风URL {self.player_cape} 已复制到剪贴板")
def open_skin_url(self):
    QDesktopServices.openUrl(QUrl(self.player_skin))
    log(f"打开皮肤URL: {self.player_skin}")
def open_cape_url(self):
    QDesktopServices.openUrl(QUrl(self.player_cape))
    log(f"打开披风URL: {self.player_cape}")
def copy_uuid_to_clipboard(self):
    clipboard = QApplication.clipboard()
    clipboard.setText(self.player_uuid)
    log(f"UUID {self.player_uuid} 已复制到剪贴板")
def copy_name_to_clipboard(self):
    clipboard = QApplication.clipboard()
    clipboard.setText(self.player_name)
    log(f"名称 {self.player_name} 已复制到剪贴板")

importlog("LINK.PY")