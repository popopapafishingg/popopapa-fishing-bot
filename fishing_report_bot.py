print("🔥 THIS IS NEW CODE 🔥")
import requests

LINE_TOKEN = "IAYqlIVl9Jh6RcvZ5C+YpHmPUv7B7uxLAU89NPSakzeS/25hb/VWjM70OvmihycYxE/C1ssd0nmdTDMTNQzlu6R6NQ95k5ccLZCuFyc19eAh1Gdx8W+hBjezZa0GdKrf+Ej+TIEaYYOd4qQBohYddQdB04t89/1O/w1cDnyilFU="

url = "https://api.line.me/v2/bot/message/push"

# 👇 ここ重要：自分に返信じゃなく broadcast
url = "https://api.line.me/v2/bot/message/broadcast"

headers = {
    "Authorization": "Bearer " + LINE_TOKEN,
    "Content-Type": "application/json",
}

data = {
    "messages": [
        {
            "type": "text",
            "text": "ブロードキャストテスト"
        }
    ],
}

r = requests.post(url, headers=headers, json=data)

print(r.status_code, r.text)
