import requests
import os

LINE_TOKEN = os.getenv("POPO_LINE_TOKEN")
USER_ID = os.getenv("USER_ID")

def send(msg):
    requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={"Authorization": f"Bearer {LINE_TOKEN}"},
        json={"to": USER_ID, "messages": [{"type": "text", "text": msg}]}
    )

def main():
    send("ポポパパAIテスト成功🔥")

if __name__ == "__main__":
    main()
