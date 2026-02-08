    def closeEvent(self, event):
        """ Override close event to minimize to tray """
        event.ignore()
        self.hide()
        # self.tray_icon.showMessage(
        #     "Fluent QQ",
        #     "程序已最小化到系统托盘",
        #     QSystemTrayIcon.MessageIcon.Information,
        #     2000
        # )

    def onMessageReceived(self, message):
        """ Handle global message notifications """
        if not config.get("enableWindowsNotification"):
            return
            
        if toast is None:
            return

        # Avoid notifying for self messages (if they ever come through here)
        # Note: We don't have self_id easily available here without checking login info
        # But typically messageReceived is for incoming.
        
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
                launch=launch_params,
                on_click=handle_reply
            )
        except Exception as e:
            print(f"[MainWindow] Toast Error: {e}")
