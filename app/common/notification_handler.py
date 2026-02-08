import urllib.parse
from .api_client import client

def handle_reply(args):
    """
    Callback for Windows Notification reply
    args example:
    {
        'arguments': 'target_id=123&is_group=True',
        'inputs': {'reply': 'Hello world'}
    }
    """
    try:
        print(f"[NotificationHandler] Received args: {args}")
        
        # 1. Parse launch arguments
        query_string = args.get('arguments', '')
        if not query_string:
            return
            
        params = dict(urllib.parse.parse_qsl(query_string))
        target_id = params.get('target_id')
        is_group_str = params.get('is_group', 'False')
        is_group = is_group_str.lower() == 'true'
        
        # 2. Get user input
        inputs = args.get('inputs', {})
        reply_text = inputs.get('reply', '')
        
        if not target_id or not reply_text:
            print("[NotificationHandler] Missing target_id or reply text")
            return
            
        # 3. Send message
        # Note: client is initialized on import, which loads config
        # Since we are in a new process (likely), config is re-loaded.
        # We use HTTP API via send_message which is stateless.
        print(f"[NotificationHandler] Sending reply to {target_id} (Group: {is_group}): {reply_text}")
        result = client.send_message(target_id, reply_text, is_group)
        print(f"[NotificationHandler] Result: {result}")
        
    except Exception as e:
        print(f"[NotificationHandler] Error: {e}")
