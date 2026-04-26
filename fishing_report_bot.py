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

# 🎯 狙い（青物）
BLUE_WORDS = [
    "サゴシ","サワラ","ブリ","メジロ","ハマチ","ツバス","ナブラ","入れ食い"
]

# 🎯 ベイト
BAIT_WORDS = [
    "アジ","サバ","イワシ","コノシロ"
]

# ❌ 消す
BAD_WORDS = [
    "入荷","商品","お知らせ","セール","イベント",
    "スタッフ","ボート","沖","船",
    "須磨","汐見","助松","公園",
    "お持ち込み","チャレ","・・・"
]

# 🎯 エリア絞り（ここ超重要）
TARGET_AREAS = [
    "貝塚","和歌山","マリーナ","田ノ浦","雑賀崎","紀ノ川","水軒"
]

def clean(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\n", "")
    text = text.strip()
    return text

def fetch(url):
    try:
        r = requests.get(url, timeout=10)
        return r.text
    except:
        return ""

def extract():
    blue_hits = []
    bait_hits = []

    for url in URLS:
        html = fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all(["a","h1","h2","h3","p"]):
            text = clean(tag.get_text())

            if len(text) < 10 or len(text) > 120:
                continue

            # ❌ ノイズ削除
            if any(b in text for b in BAD_WORDS):
                continue

            # 🎯 エリア限定
            if not any(area in text for area in TARGET_AREAS):
                continue

            # 🎯 青物優先
            if any(w in text for w in BLUE_WORDS):
                blue_hits.append(text)
                continue

            # 🎯 ベイト
            if any(w in text for w in BAIT_WORDS):
                bait_hits.append(text)

    # 重複削除
    def uniq(lst):
        out = []
        for x in lst:
            if x not in out:
                out.append(x)
        return out

    return uniq(blue_hits)[:5], uniq(bait_hits)[:5]

def short(text):
    return text[:45] + "…" if len(text) > 45 else text

def make_report(blue, bait):
    now = datetime.now().strftime("%m/%d %H:%M")

    if blue:
        body = "\n".join([f"・{short(x)}" for x in blue])
        return f"""【ポポパパ釣果AI】
更新：{now}

🔥青物気配あり🔥

{body}

結論：
今行く価値あり
ブリやで🔥"""

    if bait:
        body = "\n".join([f"・{short(x)}" for x in bait])
        return f"""【ポポパパ釣果AI】
更新：{now}

青物気配：なし
ベイトあり

{body}

結論：
ベイト付き待ちでワンチャン
ブリやで（まだ来てへん）"""

    return f"""【ポポパパ釣果AI】
更新：{now}

気配なし

結論：
今日は様子見や
ブリやで（来てへん）"""

def send(msg):
    requests.post(
        "https://api.line.me/v2/bot/message/broadcast",
        headers={
            "Authorization": f"Bearer {LINE_TOKEN}",
            "Content-Type": "application/json",
        },
        json={"messages":[{"type":"text","text":msg}]}
    )

def main():
    blue, bait = extract()
    msg = make_report(blue, bait)
    print(msg)
    send(msg)

if __name__ == "__main__":
    main()
