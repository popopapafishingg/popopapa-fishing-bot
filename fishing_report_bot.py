import requests
import os
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

VERSION = "BALANCE_FINAL_20260427"
LINE_TOKEN = os.getenv("POPO_LINE_TOKEN")

URLS = [
    "https://f-marunishi.com/fishing/fishingcat/sea",
    "https://fishingmax.co.jp/fishingpost/",
]

# 🎯 青物（厳しく）
BLUE_WORDS = [
    "サゴシ", "サワラ", "ブリ", "メジロ", "ハマチ", "ツバス"
]

# 🎯 ベイト（広く）
BAIT_WORDS = [
    "アジ", "マアジ", "サバ", "イワシ", "カタクチ", "コノシロ", "サヨリ"
]

# 🎯 軽くエリア（完全限定じゃない）
GOOD_AREAS = [
    "貝塚", "和歌山", "マリーナ", "田ノ浦", "雑賀崎", "紀ノ川"
]

# ❌ 最低限のゴミだけ除外
BAD_WORDS = [
    "入荷", "商品", "お知らせ", "セール", "イベント",
    "スタッフ釣行", "募集", "営業時間",
    "神戸", "舞子", "須磨", "六甲",
    "船", "ボート", "沖", "イカダ"
]

def clean(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def fetch(url):
    try:
        return requests.get(url, timeout=10).text
    except:
        return ""

def has_old_date(text):
    dates = re.findall(r"20\d{2}/\d{2}/\d{2}", text)
    if not dates:
        return False

    today = datetime.now()
    ok = {
        today.strftime("%Y/%m/%d"),
        (today - timedelta(days=1)).strftime("%Y/%m/%d"),
    }
    return any(d not in ok for d in dates)

def uniq(lst):
    out = []
    for x in lst:
        if x not in out:
            out.append(x)
    return out

def short(t):
    return t[:50] + "…" if len(t) > 50 else t

def extract():
    blue = []
    bait = []

    for url in URLS:
        soup = BeautifulSoup(fetch(url), "html.parser")

        for tag in soup.find_all(["a","h1","h2","h3","p"]):
            text = clean(tag.get_text())

            if len(text) < 12 or len(text) > 160:
                continue

            if any(b in text for b in BAD_WORDS):
                continue

            if has_old_date(text):
                continue

            is_blue = any(w in text for w in BLUE_WORDS)
            is_bait = any(w in text for w in BAIT_WORDS)
            area = any(a in text for a in GOOD_AREAS)

            # 🔥 青物（エリアありのみ）
            if is_blue and area:
                blue.append(text)
                continue

            # 🛟 ベイトは広く拾う（エリア関係なし）
            if is_bait:
                bait.append(text)

    return uniq(blue)[:3], uniq(bait)[:3]

def make_report(blue, bait):
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

    if bait:
        body = "\n".join([f"・{short(x)}" for x in bait])
        return f"""【ポポパパ釣果AI】
{VERSION}
更新：{now}

青物気配：なし
ベイトあり

{body}

結論：
ベイト付き待ちでワンチャン
ブリやで（まだ来てへん）"""

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
        json={"messages":[{"type":"text","text":msg}]}
    )
    print("送信結果:", r.status_code, r.text)

def main():
    print("起動:", VERSION)
    blue, bait = extract()
    print("青物件数:", len(blue))
    print("ベイト件数:", len(bait))

    msg = make_report(blue, bait)
    print(msg)
    send(msg)

if __name__ == "__main__":
    main()
