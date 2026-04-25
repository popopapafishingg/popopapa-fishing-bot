import requests

LINE_TOKEN = "ここにトークンそのまま貼る"
USER_ID = "U7fe227607853d00dc5b4d9614f4761ab"

url = "https://api.line.me/v2/bot/message/push"
headers = {
    "Authorization": f"Bearer {LINE_TOKEN}",
    "Content-Type": "application/json",
}
data = {
    "to": USER_ID,
    "messages": [{"type": "text", "text": "ポポパパ釣果AIテスト送信"}],
}

r = requests.post(url, headers=headers, json=data)
print(r.status_code, r.text)
