import requests
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup

VERSION = "FILTER_VERSION_20260426_0938"
LINE_TOKEN = os.getenv("POPO_LINE_TOKEN")

URLS = [
    "https://f-marunishi.com/fishing/fishingcat/sea",
    "https://fishingmax.co.jp/fishingpost/",
]

BLUE_WORDS = [
    "サゴシ", "サワラ", "ブリ", "メジロ", "ハマチ", "ツバス",
    "ナブラ", "入れ食い", 
]

BAIT_WORDS = [
    "アジ", "マアジ", "サバ", "イワシ", "カタクチ", "コノシロ", "サヨリ", "ベイト"
]

GOOD_AREAS = [
    "貝塚", "貝塚人工島", "和歌山", "マリーナ", "田ノ浦",
    "雑賀崎", "紀ノ川", "水軒", "加太", "衣奈", "中紀"
]

BAD_WORDS = [
    "釣果情報", "海釣り 釣果情報", "川釣り 釣果情報",
    "入荷", "商品", "お知らせ", "セール", "イベント", "営業時間",
    "スタッフ募集", "アジング・メバリング", "ロックフィッシュ",
    "南芦屋浜", "須磨", "六甲", "船", "ボート", "沖", "イカダ",
    "チャレ", "・・・", "..."
]

BAD_EXACT = [
    "釣果情報（海釣り）",
    "海釣り 釣果情報",
    "川釣り 釣果情報",
]

def clean(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\n", " ")
    text = text.replace("　", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def fetch(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=15)
        return r.text
    except Exception as e:
        print("FETCH ERROR:", e)
        return ""

def uniq(items):
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out

def short(text):
    return text[:60] + "…" if len(text) > 60 else text

def is_bad(text):
    if text in BAD_EXACT:
        return True
    if any(bad in text for bad in BAD_WORDS):
        return True
    return False

def extract():
    blue = []
    bait_good = []
    bait_any = []

    for url in URLS:
        html = fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all(["a", "h1", "h2", "h3", "p"]):
            text = clean(tag.get_text(" ", strip=True))

            if len(text) < 10 or len(text) > 160:
                continue

            if is_bad(text):
                continue

            area = any(a in text for a in GOOD_AREAS)
            is_blue = any(w in text for w in BLUE_WORDS)
            is_bait = any(w in text for w in BAIT_WORDS)

            if is_blue:
                blue.append(text)
                continue

            if is_bait and area:
                bait_good.append(text)
                continue

            if is_bait:
                bait_any.append(text)

    return uniq(blue)[:3], uniq(bait_good)[:3], uniq(bait_any)[:2]

def make_report(blue, bait_good, bait_any):
    now = datetime.now().strftime("%m/%d %H:%M")

    if blue:
        body = "\n".join([f"・{short(x)}" for x in blue])
        return f"""【ポポパパ釣果AI】
{VERSION}
更新：{now}

🔥青物気配あり🔥

{body}

結論：
朝マズメ勝負
ブリやで🔥"""

    if bait_good:
        body = "\n".join([f"・{short(x)}" for x in bait_good])
        return f"""【ポポパパ釣果AI】
{VERSION}
更新：{now}

青物気配：なし
ベイトあり

{body}

結論：
ベイト付き待ちでワンチャン
ブリやで（まだ来てへん）"""

    if bait_any:
        body = "\n".join([f"・{short(x)}" for x in bait_any])
        return f"""【ポポパパ釣果AI】
{VERSION}
更新：{now}

青物気配：なし
参考ベイトあり

{body}

結論：
完全無風ではない
ブリやで（まだ遠い）"""

    return f"""【ポポパパ釣果AI】
{VERSION}
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
    print(VERSION)
    blue, bait_good, bait_any = extract()
    print("青物:", blue)
    print("対象ベイト:", bait_good)
    print("参考ベイト:", bait_any)
    msg = make_report(blue, bait_good, bait_any)
    print(msg)
    send(msg)

if __name__ == "__main__":
    main()
