import os
import requests
from datetime import datetime, timedelta

LINE_TOKEN = os.getenv("LINE_TOKEN")
USER_ID = os.getenv("USER_ID")

def send_line(text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": text}],
    }
    r = requests.post(url, headers=headers, json=data)
    print(r.status_code, r.text)

def main():
    text = "ポポパパ釣果AIテスト送信"
    send_line(text)

if __name__ == "__main__":
    main()
