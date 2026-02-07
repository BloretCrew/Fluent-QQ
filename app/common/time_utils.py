import time
from datetime import datetime

def get_relative_time(timestamp):
    """
    Convert unix timestamp to relative time string (e.g. "5 minutes ago")
    """
    if not timestamp:
        return ""
        
    try:
        ts = int(timestamp)
        now = int(time.time())
        diff = now - ts
        
        if diff < 60:
            return "刚刚"
        elif diff < 3600:
            return f"{diff // 60}分钟前"
        elif diff < 86400:
            return f"{diff // 3600}小时前"
        elif diff < 604800:
            return f"{diff // 86400}天前"
        else:
            dt = datetime.fromtimestamp(ts)
            return dt.strftime("%Y-%m-%d")
    except Exception:
        return ""
