import requests
import os
from datetime import datetime

LINE_TOKEN = os.getenv("POPO_LINE_TOKEN")

URLS = [
    "https://f-marunishi.com/fishing/",
    "https://anglers.jp/",
]

KEYWORDS = [
    "サゴシ","サワラ","ブリ","メジロ","ハマチ","ツバス","ナブラ","入れ食い"
]

def fetch(url):
    try:
        r = requests.get(url, timeout=10)
        return r.text
    except:
        return ""

def extract():
    hits = []
    for url in URLS:
        html = fetch(url)
        for line in html.split("\n"):
            if any(k in line for k in KEYWORDS):
                hits.append(line.strip())
    return list(set(hits))[:5]

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
        body = "\n".join([f"・{h[:50]}" for h in hits])
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
