import os
import requests
from datetime import datetime, timedelta

LINE_TOKEN = os.getenv("LINE_TOKEN", "").strip()
USER_ID = os.getenv("USER_ID", "").strip()

def now_jst():
    return datetime.utcnow() + timedelta(hours=9)

def send_line(text):
    if not LINE_TOKEN or not USER_ID:
        raise ValueError("LINE_TOKEN または USER_ID が未設定")

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "to": USER_ID,
        "messages": [
            {
                "type": "text",
                "text": text,
            }
        ],
    }

    r = requests.post(url, headers=headers, json=data, timeout=30)
    print(r.status_code)
    print(r.text)

    if r.status_code >= 300:
        raise RuntimeError("LINE送信失敗")

def main():
    text = f"ポポパパ釣果AIテスト送信\nRailwayからLINE成功\n{now_jst().strftime('%Y/%m/%d %H:%M')}"
    send_line(text)
    print("DONE")

if __name__ == "__main__":
    main()
