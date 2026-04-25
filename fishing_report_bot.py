import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

LINE_TOKEN = "IAYqlIVl9Jh6RcvZ5C+YpHmPUv7B7uxLAU89NPSakzeS/25hb/VWjM70OvmihycYxE/C1ssd0nmdTDMTNQzlu6R6NQ95k5ccLZCuFyc19eAh1Gdx8W+hBjezZa0GdKrf+Ej+TIEaYYOd4qQBohYddQdB04t89/1O/w1cDnyilFU="

USER_ID = "Uf7e227607853d00dc5b4d9614f4761ab"

URLS = [
    "https://fishingmax.co.jp/fishingpost/",
]

def fetch_page(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=20)
        return r.text
    except Exception as e:
        print("ERROR:", e)
        return ""

def extract_hits():
    hits = []

    html = fetch_page(URLS[0])
    soup = BeautifulSoup(html, "html.parser")

    articles = soup.select("h3")

    for a in articles:
        text = a.get_text(strip=True)

        if len(text) < 10:
            continue

        # 🔥 青物だけ残す
        if any(word in text for word in [
            "サゴシ", "サワラ", "ブリ", "メジロ", "ハマチ", "ツバス"
        ]):
            hits.append(text)

    # 重複削除
    clean = []
    for h in hits:
        if h not in clean:
            clean.append(h)

    return clean[:5]
    
def judge_report(hits):
    now = datetime.now().strftime("%m/%d %H:%M")

    if not hits:
        return f"""【ポポパパ釣果AI】
更新：{now}

釣果情報なし

結論：
今日は完全に様子見や
ブリやで（来てへん）"""

    body = "\n".join([f"・{h}" for h in hits])

    return f"""【ポポパパ釣果AI】
更新：{now}

直近釣果：
{body}

結論：
今日は様子見〜ワンチャン
ブリやで"""

def send_line(text):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Authorization": "Bearer " + LINE_TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "messages": [{"type": "text", "text": text[:4500]}],
    }

    r = requests.post(url, headers=headers, json=data)
    print(r.status_code, r.text)

def main():
    hits = extract_hits()
    report = judge_report(hits)
    send_line(report)

if __name__ == "__main__":
    main()
