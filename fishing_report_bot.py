import requests
from datetime import datetime

LINE_TOKEN = "POPO_LINE_TOKEN="IAYqlIVl9Jh6RcvZ5C+YpHmPUv7B7uxLAU89NPSakzeS/25hb/VWjM70OvmihycYxE/C1ssd0nmdTDMTNQzlu6R6NQ95k5ccLZCuFyc19eAh1Gdx8W+hBjezZa0GdKrf+Ej+TIEaYYOd4qQBohYddQdB04t89/1O/w1cDnyilFU="
USER_ID = "U7fe227607853d00dc5b4d9614f4761ab"

def send_line(text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": "Bearer " + LINE_TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": text}],
    }

    r = requests.post(url, headers=headers, json=data, timeout=30)
    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)

    r.raise_for_status()

# 🔥 釣果AIロジック（今は簡易版）
def create_report():
    now = datetime.now().strftime("%m/%d %H:%M")

    report = f"""
【ポポパパ釣果AI】
更新：{now}

■和歌山マリーナシティ
モード：渋い
スコア：25点 → 厳しい
直近2日：釣果なし
ベイト：気配なし

■貝塚人工島
モード：渋い
スコア：25点 → 厳しい
直近2日：釣果なし

結論：
無理せず様子見推奨
"""

    return report

def main():
    text = create_report()
    send_line(text)
    print("DONE")

if __name__ == "__main__":
    main()
