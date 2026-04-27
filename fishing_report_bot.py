import requests
import os
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

VERSION = "AREA_FILTER_FINAL_20260427_0315"
LINE_TOKEN = os.getenv("POPO_LINE_TOKEN")

URLS = [
    "https://f-marunishi.com/fishing/fishingcat/sea",
    "https://fishingmax.co.jp/fishingpost/",
]

# 🎯 青物（魚名だけ）
BLUE_WORDS = [
    "サゴシ", "サワラ", "ブリ", "メジロ", "ハマチ", "ツバス"
]

# 🎯 ベイト
BAIT_WORDS = [
    "アジ", "マアジ", "サバ", "イワシ", "カタクチ", "コノシロ", "サヨリ"
]

# 🎯 ここが最重要（この中しか拾わない）
GOOD_AREAS = [
    "貝塚", "貝塚人工島",
    "和歌山", "マリーナ", "マリーナシティ",
    "田ノ浦", "雑賀崎", "紀ノ川", "水軒",
    "加太", "衣奈", "中紀"
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
    except:
        return ""

def uniq(items):
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out

def short(text):
    return text[:60] + "…" if len(text) > 60 else text

def has_old_date(text):
    dates = re.findall(r"20\d{2}/\d{2}/\d{2}", text)
    if not dates:
        return False

    today = datetime.now()
    ok = {
        today.strftime("%Y/%m/%d"),
        (today - timedelta(days=1)).strftime("%Y/%m/%d"),
    }

    for d in dates:
        if d not in ok:
            return True
    return False

def extract():
    blue = []
    bait = []

    for url in URLS:
        html = fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all(["a","h1","h2","h3","p"]):
            text = clean(tag.get_text(" ", strip=True))

            if len(text) < 12 or len(text) > 180:
                continue

            # 🔥 エリア限定（最重要）
            if not any(a in text for a in GOOD_AREAS):
                continue

            # 🔥 古い日付カット
            if has_old_date(text):
                continue

            is_blue = any(w in text for w in BLUE_WORDS)
            is_bait = any(w in text for w in BAIT_WORDS)

            if is_blue:
                blue.append(text)
                continue

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
