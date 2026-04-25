import requests
from datetime import datetime

LINE_TOKEN = "IAYqlIVl9Jh6RcvZ5C+YpHmPUv7B7uxLAU89NPSakzeS/25hb/VWjM70OvmihycYxE/C1ssd0nmdTDMTNQzlu6R6NQ95k5ccLZCuFyc19eAh1Gdx8W+hBjezZa0GdKrf+Ej+TIEaYYOd4qQBohYddQdB04t89/1O/w1cDnyilFU="

def send_line(text):
    url = "https://api.line.me/v2/bot/message/broadcast"

    headers = {
        "Authorization": "Bearer " + LINE_TOKEN,
        "Content-Type": "application/json",
    }

    data = {
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ],
    }

    r = requests.post(url, headers=headers, json=data)
    print(r.status_code, r.text)


def create_report():
    now = datetime.now().strftime("%m/%d %H:%M")

    return f"""【ポポパパ釣果AI】
更新：{now}

■和歌山マリーナシティ
モード：渋い
→ サゴシ厳しい

■貝塚人工島
モード：渋い

結論：
今日は無理せん方がええ日やで
ブリやで（来てへん）"""


def main():
    text = create_report()
    send_line(text)


import os

if __name__ == "__main__":
    if os.getenv("RUN_MODE") == "cron":
        main()
    else:
        print("起動のみ（送信しない）")
.
