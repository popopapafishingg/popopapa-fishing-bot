import os
import requests

def clean_env(name):
    v = os.getenv(name, "")
    v = v.strip().strip('"').strip("'")
    v = v.replace("\n", "").replace("\r", "").replace(" ", "")
    if "=" in v:
        v = v.split("=", 1)[1]
    return v

LINE_TOKEN = clean_env("POPO_LINE_TOKEN")
USER_ID = clean_env("USER_ID")

print("POPO_LINE_TOKEN length:", len(LINE_TOKEN))
print("USER_ID length:", len(USER_ID))

print("TOKEN length:", len(LINE_TOKEN))
print("USER_ID:", USER_ID)
print("USER_ID length:", len(USER_ID))

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

    r = requests.post(url, headers=headers, json=data, timeout=30)
    print(r.status_code, r.text)

    if r.status_code >= 300:
        raise RuntimeError("LINE送信失敗")

send_line("ポポパパ釣果AIテスト送信")
print("DONE")
