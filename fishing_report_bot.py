import requests
import os
from datetime import datetime
from bs4 import BeautifulSoup

LINE_TOKEN = os.getenv("POPO_LINE_TOKEN")

URL = "https://f-marunishi.com/fishing/fishingcat/sea"

KEYWORDS = ["サゴシ","サワラ","ブリ","メジロ","ハマチ","ツバス","ナブラ","入れ食い"]
BAD_WORDS = ["入荷","お知らせ","セール","商品","イベント"]

def fetch():
    try:
        r = requests.get(URL, timeout=10)
        return r.text
    except:
        return ""

def extract():
    html = fetch()
    soup = BeautifulSoup(html, "html.parser")

    hits = []

    for a in soup.find_all("a"):
        text = a.get_text(strip=True)

        if len(text) < 10 or len(text) > 100:
            continue

        # ゴミ除去
        if any(b in text for b in BAD_WORDS):
            continue

        # 青物系だけ
        if any(k in text for k in KEYWORDS):
            hits.append(text)

    return list(dict.fromkeys(hits))[:5]

def send(msg):
    requests.post(
        "https://api.line.me/v2/bot/message/broadcast",
        headers={
            "Authorization": f"Bearer {LINE_TOKEN}",
            "Content-Type": "application/json",
        },
        json={"messages": [{"type": "text", "text": msg}]}
    )

def main():
    hits = extract()
    now = datetime.now().strftime("%m/%d %H:%M")

    if not hits:
        msg = f"""【ポポパパ釣果AI】
更新：{now}

青物気配なし

結論：
今日は様子見や
ブリやで（来てへん）"""
    else:
        body = "\n".join([f"・{h}" for h in hits])

        msg = f"""【ポポパパ釣果AI】
更新：{now}

直近気配：
{body}

結論：
ワンチャンある
ブリやで🔥"""

    send(msg)

if __name__ == "__main__":
    main()
