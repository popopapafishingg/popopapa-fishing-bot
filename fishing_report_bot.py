import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

LINE_TOKEN = "IAYqlIVl9Jh6RcvZ5C+YpHmPUv7B7uxLAU89NPSakzeS/25hb/VWjM70OvmihycYxE/C1ssd0nmdTDMTNQzlu6R6NQ95k5ccLZCuFyc19eAh1Gdx8W+hBjezZa0GdKrf+Ej+TIEaYYOd4qQBohYddQdB04t89/1O/w1cDnyilFU="

USER_ID = "Uf7e227607853d00dc5b4d9614f4761ab"

URL = "https://kanpuri.com/choka/"

def fetch():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers)
    return r.text

def extract():
    html = fetch()
    soup = BeautifulSoup(html, "html.parser")

    hits = []

    for a in soup.select("a"):
        text = a.get_text(strip=True)

        if len(text) < 15 or len(text) > 120:
            continue

        if any(word in text for word in [
            "サゴシ", "サワラ", "ブリ", "メジロ", "ハマチ", "ツバス"
        ]):
            hits.append(text)

    return list(dict.fromkeys(hits))[:10]

def report(hits):
    now = datetime.now().strftime("%m/%d %H:%M")

    if not hits:
        return f"""【ポポパパ釣果AI】
更新：{now}

青物気配なし
今日は様子見や
ブリやで（来てへん）"""

    body = "\n".join([f"・{h}" for h in hits])

    return f"""【ポポパパ釣果AI】
更新：{now}

直近青物：
{body}

結論：
チャンスあり
ブリやで🔥"""

def send(text):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Authorization": "Bearer " + LINE_TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "messages": [{"type": "text", "text": text}]
    }
    requests.post(url, headers=headers, json=data)

def main():
    hits = extract()
    text = report(hits)
    send(text)

if __name__ == "__main__":
    main()
