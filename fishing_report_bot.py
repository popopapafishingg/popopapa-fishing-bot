import requests
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup

LINE_TOKEN = os.getenv("POPO_LINE_TOKEN")

URLS = [
    "https://f-marunishi.com/fishing/fishingcat/sea",
    "https://fishingmax.co.jp/fishingpost/",
]

KEYWORDS = [
    "サゴシ", "サワラ", "ブリ", "メジロ", "ハマチ", "ツバス",
    "ナブラ", "なぶら", "入れ食い"
]

BAD_WORDS = [
    "入荷", "新商品", "商品", "お知らせ", "セール", "イベント",
    "マルキュー", "エサコーナー", "営業時間", "スタッフ募集",
    "<a", "<h2", "href=", "class="
]

def clean_text(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.strip()
    return text

def fetch(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print("FETCH ERROR:", url, e)
        return ""

def extract():
    hits = []

    for url in URLS:
        html = fetch(url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all(["a", "h1", "h2", "h3", "p"]):
            text = clean_text(tag.get_text(" ", strip=True))

            if len(text) < 8 or len(text) > 120:
                continue

            if any(bad in text for bad in BAD_WORDS):
                continue

            if any(key in text for key in KEYWORDS):
                hits.append(text)

    clean = []
    for h in hits:
        if h not in clean:
            clean.append(h)

    return clean[:8]

def make_report(hits):
    now = datetime.now().strftime("%m/%d %H:%M")

    if not hits:
        return f"""【ポポパパ釣果AI】
更新：{now}

青物気配なし

結論：
今日は様子見や
ブリやで（来てへん）"""

    body = "\n".join([f"・{h}" for h in hits])

    return f"""【ポポパパ釣果AI】
更新：{now}

直近気配：
{body}

結論：
ワンチャンある
ブリやで🔥"""

def send_line(text):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messages": [{"type": "text", "text": text[:4500]}]
    }

    r = requests.post(url, headers=headers, json=data, timeout=30)
    print("送信結果:", r.status_code, r.text)

def main():
    print("ポポパパ釣果AI 起動")
    hits = extract()
    print("取得件数:", len(hits))
    report = make_report(hits)
    print(report)
    send_line(report)

if __name__ == "__main__":
    main()
