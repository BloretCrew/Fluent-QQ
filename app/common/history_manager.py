import sqlite3
import os
import json
import time
import zlib
from PyQt6.QtCore import QObject

class HistoryManager(QObject):
    """ Local History Persistence Manager """
    
    def __init__(self, user_id="common"):
        super().__init__()
        self.user_id = user_id
        self.db_path = self._get_db_path()
        self._init_db()

    def set_user_id(self, user_id):
        if self.user_id != user_id:
            self.user_id = user_id
            self.db_path = self._get_db_path()
            self._init_db()

    def _get_db_path(self):
        appdata = os.environ.get("APPDATA")
        # Ensure path exists
        base = os.path.join(appdata, "Fluent-QQ", "history", str(self.user_id))
        if not os.path.exists(base):
            os.makedirs(base, exist_ok=True)
        return os.path.join(base, "chat_history.db")

    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            # Enable memory mapping for faster access
            conn.execute("PRAGMA mmap_size = 30000000000")
            c = conn.cursor()
            
            # Meta table for versioning
            c.execute('''CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)''')
            c.execute('''INSERT OR IGNORE INTO meta (key, value) VALUES ('version', '1.1')''')
            
            # Messages table
            # raw_data stored as BLOB (zlib compressed)
            c.execute('''CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                target_id TEXT,
                is_group INTEGER,
                sender_id TEXT,
                time INTEGER,
                content TEXT,
                raw_data BLOB
            )''')
            
            # Index for fast query by target (chat session) and time
            c.execute('''CREATE INDEX IF NOT EXISTS idx_target_time ON messages (target_id, is_group, time DESC)''')
            
            conn.commit()
            conn.close()
            print(f"[History] DB initialized at {self.db_path}")
        except Exception as e:
            print(f"[History] Init error: {e}")

    def save_message(self, target_id, is_group, msg_data):
        """ Save or update a message """
        if not msg_data: return
        
        try:
            msg_id = str(msg_data.get("message_id"))
            sender_id = str(msg_data.get("sender", {}).get("user_id", ""))
            timestamp = msg_data.get("time", int(time.time()))
            
            # Content handling: if list, json dump; if string, keep
            content_raw = msg_data.get("message", "")
            if isinstance(content_raw, list) or isinstance(content_raw, dict):
                content = json.dumps(content_raw, ensure_ascii=False)
            else:
                content = str(content_raw)
                
            # Compress raw_data
            raw_json = json.dumps(msg_data, ensure_ascii=False).encode('utf-8')
            raw_blob = zlib.compress(raw_json)
            
            conn = sqlite3.connect(self.db_path)
            # Enable memory mapping
            conn.execute("PRAGMA mmap_size = 30000000000")
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO messages (message_id, target_id, is_group, sender_id, time, content, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (msg_id, str(target_id), 1 if is_group else 0, sender_id, timestamp, content, raw_blob))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[History] Save error: {e}")

    def save_messages(self, target_id, is_group, messages):
        """ Batch save messages """
        if not messages: return
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA mmap_size = 30000000000")
            c = conn.cursor()
            
            data_list = []
            for msg in messages:
                msg_id = str(msg.get("message_id"))
                sender_id = str(msg.get("sender", {}).get("user_id", ""))
                timestamp = msg.get("time", int(time.time()))
                
                content_raw = msg.get("message", "")
                if isinstance(content_raw, list) or isinstance(content_raw, dict):
                    content = json.dumps(content_raw, ensure_ascii=False)
                else:
                    content = str(content_raw)
                
                raw_json = json.dumps(msg, ensure_ascii=False).encode('utf-8')
                raw_blob = zlib.compress(raw_json)
                
                data_list.append((msg_id, str(target_id), 1 if is_group else 0, sender_id, timestamp, content, raw_blob))
            
            c.executemany('''
                INSERT OR REPLACE INTO messages (message_id, target_id, is_group, sender_id, time, content, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', data_list)
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[History] Batch save error: {e}")

    def get_messages(self, target_id, is_group, limit=50, offset=0):
        """ Get messages from local DB """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA mmap_size = 30000000000")
            c = conn.cursor()
            
            c.execute('''
                SELECT raw_data FROM messages 
                WHERE target_id = ? AND is_group = ? 
                ORDER BY time DESC 
                LIMIT ? OFFSET ?
            ''', (str(target_id), 1 if is_group else 0, limit, offset))
            
            rows = c.fetchall()
            conn.close()
            
            messages = []
            for row in rows:
                if row[0]:
                    try:
                        # Try decompressing
                        decompressed = zlib.decompress(row[0])
                        messages.append(json.loads(decompressed.decode('utf-8')))
                    except Exception:
                        # Fallback for uncompressed data (migration support)
                        try:
                            if isinstance(row[0], str):
                                messages.append(json.loads(row[0]))
                            else:
                                messages.append(json.loads(row[0].decode('utf-8')))
                        except:
                            pass
            
            # Return in chronological order (oldest first)
            return messages[::-1]
            
        except Exception as e:
            print(f"[History] Load error: {e}")
            return []

    def get_message_by_id(self, message_id):
        """ Get a single message by ID """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA mmap_size = 30000000000")
            c = conn.cursor()
            
            c.execute('SELECT raw_data FROM messages WHERE message_id = ?', (str(message_id),))
            row = c.fetchone()
            conn.close()
            
            if row and row[0]:
                try:
                    decompressed = zlib.decompress(row[0])
                    return json.loads(decompressed.decode('utf-8'))
                except:
                    # Fallback
                    try:
                        return json.loads(row[0]) if isinstance(row[0], str) else json.loads(row[0].decode('utf-8'))
                    except:
                        pass
            return None
        except Exception as e:
            print(f"[History] Get message error: {e}")
            return None

history_manager = HistoryManager()
