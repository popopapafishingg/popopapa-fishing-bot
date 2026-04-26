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
    "サゴシ", "サワラ", "ブリ", "メジロ", "ハマチ", "ツバス"
]

NABRA_WORDS = [
    "ナブラ", "なぶら", "入れ食い", "ボイル", "沸き", "湧き"
]

BAIT_WORDS = [
    "アジ", "マアジ", "サバ", "イワシ", "カタクチ", "コノシロ", "サヨリ", "ベイト"
]

BAD_WORDS = [
    "入荷", "新商品", "商品", "お知らせ", "セール", "イベント",
    "スタッフ", "ボート", "沖", "船", "須磨", "汐見", "助松",
    "公園", "お持ち込み", "チャレ", "・・・", "...",
    "営業時間", "募集", "エサコーナー"
]

TARGET_AREAS = [
    "貝塚", "貝塚人工島",
    "和歌山", "マリーナ", "和歌山マリーナシティ",
    "田ノ浦", "雑賀崎", "紀ノ川", "水軒",
    "加太", "衣奈", "由良", "湯浅", "海南"
]

def clean(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\n", "")
    text = text.replace("　", " ")
    return text.strip()

def fetch(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=15)
        return r.text
    except Exception as e:
        print("FETCH ERROR:", e)
        return ""

def unique(items):
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out

def extract():
    nabra_hits = []
    blue_hits = []
    bait_hits = []

    for url in URLS:
        html = fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all(["a", "h1", "h2", "h3", "p"]):
            text = clean(tag.get_text(" ", strip=True))

            if len(text) < 8 or len(text) > 130:
                continue

            if any(bad in text for bad in BAD_WORDS):
                continue

            area_hit = any(area in text for area in TARGET_AREAS)
            nabra_hit = any(w in text for w in NABRA_WORDS)
            blue_hit = any(w in text for w in BLUE_WORDS)
            bait_hit = any(w in text for w in BAIT_WORDS)

            if nabra_hit and (area_hit or blue_hit):
                nabra_hits.append(text)
                continue

            if blue_hit and area_hit:
                blue_hits.append(text)
                continue

            if bait_hit and area_hit:
                bait_hits.append(text)

    return unique(nabra_hits)[:5], unique(blue_hits)[:5], unique(bait_hits)[:5]

def short(text):
    return text[:55] + "…" if len(text) > 55 else text

def make_report(nabra, blue, bait):
    now = datetime.now().strftime("%m/%d %H:%M")

    if nabra:
        body = "\n".join([f"・{short(x)}" for x in nabra])
        return f"""【ポポパパ釣果AI】
更新：{now}

🔥爆釣モード🔥
ナブラ・湧き気配あり

{body}

結論：
今すぐ行く価値あり
ジグ・ブレード・セットアッパー準備
ブリやで🔥"""

    if blue:
        body = "\n".join([f"・{short(x)}" for x in blue])
        return f"""【ポポパパ釣果AI】
更新：{now}

青物気配あり🔥

{body}

結論：
朝マズメ勝負
ワンチャンあるで
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
    r = requests.post(
        "https://api.line.me/v2/bot/message/broadcast",
        headers={
            "Authorization": f"Bearer {LINE_TOKEN}",
            "Content-Type": "application/json",
        },
        json={"messages": [{"type": "text", "text": msg[:4500]}]},
        timeout=30,
    )
    print("送信結果:", r.status_code, r.text)

def main():
    print("ポポパパ釣果AI 起動")
    nabra, blue, bait = extract()
    print("ナブラ件数:", len(nabra))
    print("青物件数:", len(blue))
    print("ベイト件数:", len(bait))
    msg = make_report(nabra, blue, bait)
    print(msg)
    send(msg)

if __name__ == "__main__":
    main()
