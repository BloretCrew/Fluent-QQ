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

    def call_api(self, action, params=None):
        """ Call HTTP API """
        try:
            url = f"{self.api_url}/{action}"
            print(f"[Client] Calling API: {url}")
            response = requests.post(url, json=params or {}, headers=self.get_api_headers(), timeout=5)
            print(f"[Client] API Response status: {response.status_code}")
            return response.json()
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

client = NapCatClient()
