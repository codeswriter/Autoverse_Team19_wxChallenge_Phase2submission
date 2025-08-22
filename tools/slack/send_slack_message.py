# Assisted by watsonx Code Assistant
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from ibm_watsonx_orchestrate.run import connections
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials
import requests, json, codecs

APP_ID="slack_webhook_connection"
CHANNEL="#autoverse-notifications"

def unescape_text(s: str) -> str:
    try:
        s2 = json.loads(f'"{s}"')
        s = s2
    except Exception:
        pass
    try:
        s2 = codecs.decode(s, "unicode_escape")
        s = s2
    except Exception:
        pass
    prev = None
    while prev != s:
        prev = s
        s = s.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\r\n", "\n")
    if "\\n" in s:
        s = "\n".join(part.replace("\\r", "") for part in s.split("\\n"))
    return s

@tool(
    name="send_slack_message",
    description="Send a message to slack using blocks (mrkdwn).",
    permission=ToolPermission.READ_ONLY,
    expected_credentials=[ExpectedCredentials(
        app_id=APP_ID,
        type=ConnectionType.KEY_VALUE
    )]
)
def send_slack_message(text: str, username: str = "Autoverse Bot"):
    """
    Send a message to #autoverse-notifications using blocks (mrkdwn).
    Converts any literal '\\n' sequences into real line breaks.
    """
    
    conn = connections.key_value(APP_ID)
    webhook_url = conn.get("webhookurl")
    
    norm = unescape_text(text)

    payload = {
        "channel": CHANNEL,
        "username": username,
        "text": "Message",  # fallback
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": norm}
            }
        ]
    }

    try:
        r = requests.post(webhook_url, json=payload, timeout=15)
        r.raise_for_status()
        return {"status": "success", "channel": CHANNEL, "http_status": r.status_code}
    except requests.exceptions.RequestException as e:
        body = getattr(e.response, "text", "")[:300] if getattr(e, "response", None) else ""
        return {"status": "error", "error": str(e), "http_status": getattr(e.response, "status_code", None), "body": body}

if __name__ == "__main__":
    msg = "*Hello*,\nThis is a test of a message sent from script.\nThank you."
    print(send_slack_message(msg))
