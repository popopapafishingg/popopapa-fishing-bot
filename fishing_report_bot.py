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

BLUE_WORDS = ["サゴシ","サワラ","ブリ","メジロ","ハマチ","ツバス"]
NABRA_WORDS = ["ナブラ","なぶら","入れ食い","ボイル"]
BAIT_WORDS = ["アジ","サバ","イワシ","コノシロ","サヨリ"]

BAD_WORDS = [
    "入荷","商品","お知らせ","セール","イベント",
    "スタッフ","ボート","沖","船",
    "須磨","汐見","助松","公園",
    "お持ち込み","チャレ","・・・"
]

TARGET_AREAS = [
    "貝塚","和歌山","マリーナ","田ノ浦","雑賀崎","紀ノ川","水軒"
]

def clean(text):
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()

def fetch(url):
    try:
        return requests.get(url, timeout=10).text
    except:
        return ""

def uniq(lst):
    out = []
    for x in lst:
        if x not in out:
            out.append(x)
    return out

def extract():
    nabra = []
    blue = []
    bait = []

    for url in URLS:
        html = fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all(["a","h1","h2","h3","p"]):
            text = clean(tag.get_text())

            if len(text) < 10 or len(text) > 120:
                continue

            if any(b in text for b in BAD_WORDS):
                continue

            area = any(a in text for a in TARGET_AREAS)

            # ナブラ（最優先）
            if any(w in text for w in NABRA_WORDS) and area:
                nabra.append(text)
                continue

            # 青物（エリア限定）
            if any(w in text for w in BLUE_WORDS) and area:
                blue.append(text)
                continue

            # ベイト（エリア無視）
            if any(w in text for w in BAIT_WORDS):
                bait.append(text)

    return uniq(nabra)[:5], uniq(blue)[:5], uniq(bait)[:5]

def short(t):
    return t[:45] + "…" if len(t) > 45 else t

def make_report(nabra, blue, bait):
    now = datetime.now().strftime("%m/%d %H:%M")

    if nabra:
        body = "\n".join([f"・{short(x)}" for x in nabra])
        return f"""【ポポパパ釣果AI】
更新：{now}

🔥爆釣モード🔥
ナブラ発生

{body}

結論：
今すぐ行け
ブリやで🔥"""

    if blue:
        body = "\n".join([f"・{short(x)}" for x in blue])
        return f"""【ポポパパ釣果AI】
更新：{now}

青物気配あり🔥

{body}

結論：
朝マズメ勝負
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
    nabra, blue, bait = extract()
    msg = make_report(nabra, blue, bait)
    print(msg)
    send(msg)

if __name__ == "__main__":
    main()
