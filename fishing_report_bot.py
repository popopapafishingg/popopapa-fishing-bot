print("🔥 THIS IS NEW CODE 🔥")
import requests

LINE_TOKEN = "IAYqlIVl9Jh6RcvZ5C+YpHmPUv7B7uxLAU89NPSakzeS/25hb/VWjM70OvmihycYxE/C1ssd0nmdTDMTNQzlu6R6NQ95k5ccLZCuFyc19eAh1Gdx8W+hBjezZa0GdKrf+Ej+TIEaYYOd4qQBohYddQdB04t89/1O/w1cDnyilFU="
USER_ID = "U7fe227607853d00dc5b4d9614f4761ab"

url = "https://api.line.me/v2/bot/message/push"

headers = {
    "Authorization": "Bearer " + LINE_TOKEN,
    "Content-Type": "application/json",
}

data = {
    "to": USER_ID,
    "messages": [
        {
            "type": "text",
            "text": "テスト"
        }
    ],
}

r = requests.post(url, headers=headers, json=data, timeout=30)
print(r.status_code, r.text)
