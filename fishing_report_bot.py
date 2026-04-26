import requests
import os

LINE_TOKEN = os.getenv("POPO_LINE_TOKEN")

print("起動OK")
print("TOKENある？", bool(LINE_TOKEN))

def send(msg):
    print("送信開始")
    r = requests.post(
        "https://api.line.me/v2/bot/message/broadcast",
        headers={
            "Authorization": f"Bearer {LINE_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "messages": [
                {"type": "text", "text": msg}
            ]
        },
        timeout=30,
    )
    print("送信結果:", r.status_code, r.text)

def main():
    print("main入った")
    send("ポポパパAIテスト成功🔥")

if __name__ == "__main__":
    main()
