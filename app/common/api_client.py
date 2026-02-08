import requests
import websocket
import json
import threading
from PyQt6.QtCore import QObject, pyqtSignal
from .config import config

class NapCatClient(QObject):
    """ NapCat QQ API Client (OneBot v11) """
    messageReceived = pyqtSignal(dict)
    connected = pyqtSignal()
    disconnected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ws = None
        self._keep_running = False
        self._refresh_config()

    def _refresh_config(self):
        self.api_url = config.get("api_url").rstrip('/')
        self.ws_url = config.get("ws_url")
        self.token = config.get("token")
        print(f"[Client] Config refreshed: API={self.api_url}, WS={self.ws_url}, Token={'***' if self.token else 'None'}")

    def get_api_headers(self):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def call_api(self, action, params=None, timeout=20):
        """ Call HTTP API """
        try:
            url = f"{self.api_url}/{action}"
            print(f"[Client] Calling API: {url}")
            response = requests.post(url, json=params or {}, headers=self.get_api_headers(), timeout=timeout)
            print(f"[Client] API Response status: {response.status_code}")
            
            data = response.json()
            
            # Check for specific error messages even if status is 200
            if isinstance(data, dict):
                if data.get("status") == "failed" or data.get("retcode") != 0:
                     msg = data.get("message") or data.get("wording")
                     print(f"[Client] API Logic Error: {msg}")
                     
                # Specific check for token failure
                if data.get("message") == "token verify failed!":
                    print("[Client] Critical: Token verification failed!")
                    # Optional: Emit signal to prompt re-login
                    
            return data
        except Exception as e:
            print(f"[Client] API Error: {e}")
            return None

    def start_ws(self):
        """ Start WebSocket connection """
        if self._keep_running:
            print("[Client] WebSocket already running")
            return
        
        self._refresh_config()
        self._keep_running = True
        self.ws_thread = threading.Thread(target=self._ws_loop, daemon=True)
        self.ws_thread.start()
        print("[Client] WebSocket thread started")

    def stop_ws(self):
        self._keep_running = False
        if self.ws:
            self.ws.close()
            self.ws = None

    def _ws_loop(self):
        print(f"[Client] Starting WS loop for {self.ws_url}")
        while self._keep_running:
            try:
                headers = []
                if self.token:
                    headers.append(f"Authorization: Bearer {self.token}")
                
                print(f"[Client] Attempting to connect to {self.ws_url}...")
                self.ws = websocket.WebSocketApp(
                    self.ws_url,
                    header=headers,
                    on_message=self._on_message,
                    on_open=self._on_open,
                    on_close=self._on_close,
                    on_error=self._on_error
                )
                self.ws.run_forever()
            except Exception as e:
                print(f"[Client] WS Loop Exception: {e}")
            
            # Reconnect delay
            if self._keep_running:
                print("[Client] WS connection lost, retrying in 5s...")
                import time
                time.sleep(5)

    def _on_message(self, ws, message):
        data = json.loads(message)
        self.messageReceived.emit(data)

    def _on_open(self, ws):
        print("WebSocket Connected")
        self.connected.emit()

    def _on_close(self, ws, close_status_code, close_msg):
        print("WebSocket Disconnected")
        self.disconnected.emit()

    def _on_error(self, ws, error):
        print(f"WebSocket Error: {error}")

    def _to_id(self, val):
        try:
            if val is None or str(val).lower() == 'none':
                return None
            return int(val)
        except (ValueError, TypeError):
            return None

    def send_message(self, target_id, message, is_group=False):
        """ Send message via HTTP API """
        tid = self._to_id(target_id)
        if tid is None:
            print(f"[Client] Invalid target_id: {target_id}")
            return None
            
        action = "send_group_msg" if is_group else "send_private_msg"
        params = {
            "group_id" if is_group else "user_id": tid,
            "message": message
        }
        return self.call_api(action, params)

    def send_image(self, target_id, image_path, is_group=False):
        """ Send image message """
        # Using base64 for remote server compatibility
        import os
        import base64
        
        if not os.path.exists(image_path):
            print(f"[Client] Image file not found: {image_path}")
            return None
            
        try:
            with open(image_path, "rb") as f:
                img_data = f.read()
                b64_data = base64.b64encode(img_data).decode('utf-8')
            
            cq_code = f"[CQ:image,file=base64://{b64_data}]"
            return self.send_message(target_id, cq_code, is_group)
        except Exception as e:
            print(f"[Client] Failed to send image: {e}")
            return None

    def upload_file(self, target_id, file_path, is_group=False):
        """ Upload file (Group or Private) """
        tid = self._to_id(target_id)
        if tid is None:
            return None
            
        import os
        if not os.path.exists(file_path):
            print(f"[Client] File not found: {file_path}")
            return None
            
        file_name = os.path.basename(file_path)
        abs_path = os.path.abspath(file_path)
        
        # Try to use base64 for remote bots
        file_param = abs_path
        try:
            import base64
            # Limit to reasonable size (e.g. 100MB) to avoid memory issues
            if os.path.getsize(abs_path) < 100 * 1024 * 1024:
                with open(abs_path, "rb") as f:
                    b64_data = base64.b64encode(f.read()).decode('utf-8')
                    file_param = f"base64://{b64_data}"
        except Exception as e:
            print(f"[Client] Failed to encode file to base64: {e}")
            # Fallback to path
            pass

        if is_group:
            action = "upload_group_file"
            params = {
                "group_id": tid,
                "file": file_param,
                "name": file_name
            }
        else:
            action = "upload_private_file"
            params = {
                "user_id": tid,
                "file": file_param,
                "name": file_name
            }
            
        return self.call_api(action, params, timeout=120)

    def delete_msg(self, message_id):
        """ Recall/Withdraw message """
        if not message_id:
            return None
        return self.call_api("delete_msg", {"message_id": message_id})

    def set_msg_emoji_like(self, message_id, emoji_id, set_like=True):
        """ Set emoji reaction on a message """
        if not message_id or not emoji_id:
            return None
        return self.call_api("set_msg_emoji_like", {
            "message_id": message_id,
            "emoji_id": str(emoji_id),
            "set": set_like
        })

    def get_msg_emoji_likes(self, message_id):
        """ Get emoji reactions for a message """
        if not message_id:
            return None
        return self.call_api("get_emoji_likes", {
            "message_id": message_id
        })

    def get_history(self, target_id, is_group=False, count=20):
        """ Get message history from NapCat """
        tid = self._to_id(target_id)
        if tid is None:
            print(f"[Client] Invalid target_id for history: {target_id}")
            return None

        action = "get_group_msg_history" if is_group else "get_private_msg_history"
        params = {
            "group_id" if is_group else "user_id": tid,
            "count": count
        }
        return self.call_api(action, params)

    def get_group_list(self):
        """ Get group list """
        return self.call_api("get_group_list")

    def get_friend_list(self):
        """ Get friend list """
        return self.call_api("get_friend_list")

    def get_recent_contact(self):
        """ Get recent contact list (NapCat extension) """
        return self.call_api("get_recent_contact")

    def get_group_member_list(self, group_id, no_cache=False):
        """ Get group member list """
        tid = self._to_id(group_id)
        if tid is None:
            return None
        return self.call_api("get_group_member_list", {"group_id": tid, "no_cache": no_cache})

    def get_login_info(self):
        """ Get login info """
        return self.call_api("get_login_info")

client = NapCatClient()
