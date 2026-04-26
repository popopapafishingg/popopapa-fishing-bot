import requests
import os

LINE_TOKEN = os.getenv("POPO_LINE_TOKEN")
USER_ID = os.getenv("USER_ID")

print("起動OK")

def send(msg):
    print("送信開始")
    r = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={"Authorization": f"Bearer {LINE_TOKEN}"},
        json={"to": USER_ID, "messages": [{"type": "text", "text": msg}]}
    )
    print("送信結果:", r.status_code, r.text)

def main():
    print("main入った")
    send("ポポパパAIテスト成功🔥")

if __name__ == "__main__":
    main()
