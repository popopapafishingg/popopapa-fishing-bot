import requests

LINE_TOKEN = "IAYqlIVl9Jh6RcvZ5C+YpHmPUv7B7uxLAU89NPSakzeS/25hb/VWjM70OvmihycYxE/C1ssd0nmdTDMTNQzlu6R6NQ95k5ccLZCuFyc19eAh1Gdx8W+hBjezZa0GdKrf+Ej+TIEaYYOd4qQBohYddQdB04t89/1O/w1cDnyilFU="
USER_ID = "Uf7e227607853d00dc5b4d9614f4761ab"

print("TOKEN length:", len(LINE_TOKEN))
print("USER_ID length:", len(USER_ID))

# 変な文字チェック
LINE_TOKEN.encode("ascii")
USER_ID.encode("ascii")

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
            "text": "ポポパパ釣果AIテスト送信成功"
        }
    ]
}

r = requests.post(url, headers=headers, json=data, timeout=30)

print("STATUS:", r.status_code)
print("RESPONSE:", r.text)

r.raise_for_status()

print("DONE")
