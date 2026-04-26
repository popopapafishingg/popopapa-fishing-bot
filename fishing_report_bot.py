print("VERSION_20260426_BAIT_TEST")
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

BLUE_WORDS = [
    "サゴシ", "サワラ", "ブリ", "メジロ", "ハマチ", "ツバス",
    "ナブラ", "なぶら", "入れ食い"
]

BAIT_WORDS = [
    "アジ", "サバ", "イワシ", "コノシロ", "ベイト", "小魚"
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
    return text.strip()

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
    blue_hits = []
    bait_hits = []

    for url in URLS:
        html = fetch(url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all(["a", "h1", "h2", "h3", "p"]):
            text = clean_text(tag.get_text(" ", strip=True))

            if len(text) < 8 or len(text) > 140:
                continue

            if any(bad in text for bad in BAD_WORDS):
                continue

            if any(word in text for word in BLUE_WORDS):
                blue_hits.append(text)
                continue

            if any(word in text for word in BAIT_WORDS):
                bait_hits.append(text)

    def unique(items):
        out = []
        for x in items:
            if x not in out:
                out.append(x)
        return out

    return unique(blue_hits)[:8], unique(bait_hits)[:8]

def make_report(blue_hits, bait_hits):
    now = datetime.now().strftime("%m/%d %H:%M")

    if blue_hits:
        body = "\n".join([f"・{h}" for h in blue_hits])
        return f"""【ポポパパ釣果AI】
更新：{now}

青物気配あり🔥

直近青物：
{body}

結論：
ワンチャンあり
ブリやで🔥"""

    if bait_hits:
        body = "\n".join([f"・{h}" for h in bait_hits])
        return f"""【ポポパパ釣果AI】
更新：{now}

青物気配：なし
ベイト・参考釣果：あり

参考情報：
{body}

結論：
青物はまだ弱いけど、ベイト次第でワンチャン
ブリやで（まだ来てへん）"""

    return f"""【ポポパパ釣果AI】
更新：{now}

青物気配なし
ベイト気配も薄い

結論：
今日は様子見や
ブリやで（来てへん）"""

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
    blue_hits, bait_hits = extract()
    print("青物件数:", len(blue_hits))
    print("参考件数:", len(bait_hits))
    report = make_report(blue_hits, bait_hits)
    print(report)
    send_line(report)

if __name__ == "__main__":
    main()
