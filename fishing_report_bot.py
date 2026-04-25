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

print("TOKEN length:", len(LINE_TOKEN))
print("USER_ID:", USER_ID)
print("USER_ID length:", len(USER_ID))
print("TEXT:", data["messages"][0]["text"])
print("TEXT length:", len(data["messages"][0]["text"]))
print("DATA:", data)

r = requests.post(url, headers=headers, json=data, timeout=30)

print("STATUS:", r.status_code)
print("RESPONSE:", r.text)
