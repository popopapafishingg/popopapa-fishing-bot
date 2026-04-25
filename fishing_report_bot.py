import os
import requests

LINE_TOKEN = os.getenv("LINE_TOKEN", "").strip()
USER_ID = os.getenv("USER_ID", "").strip()

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
        "messages": [{"type": "text", "text": text}],
    }

    r = requests.post(url, headers=headers, json=data, timeout=30)
    print(r.status_code, r.text)

    if r.status_code >= 300:
        raise RuntimeError("LINE送信失敗")

def main():
    send_line("ポポパパ釣果AIテスト送信")
    print("DONE")

if __name__ == "__main__":
    main()
