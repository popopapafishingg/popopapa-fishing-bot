import requests
import os
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

VERSION = "AREA_FILTER_SEND_CHECK_20260427"
LINE_TOKEN = os.getenv("POPO_LINE_TOKEN")

URLS = [
    "https://f-marunishi.com/fishing/fishingcat/sea",
    "https://fishingmax.co.jp/fishingpost/",
]

BLUE_WORDS = ["サゴシ", "サワラ", "ブリ", "メジロ", "ハマチ", "ツバス"]
BAIT_WORDS = ["アジ", "マアジ", "サバ", "イワシ", "カタクチ", "コノシロ", "サヨリ"]

GOOD_AREAS = [
    "貝塚", "貝塚人工島", "和歌山", "マリーナ", "マリーナシティ",
    "田ノ浦", "雑賀崎", "紀ノ川", "水軒", "加太", "衣奈", "中紀"
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
        return requests.get(url, headers=headers, timeout=15).text
    except Exception as e:
        print("FETCH ERROR:", url, e)
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

def uniq(items):
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out

def short(text):
    return text[:60] + "…" if len(text) > 60 else text

def extract():
    blue = []
    bait = []

    for url in URLS:
        soup = BeautifulSoup(fetch(url), "html.parser")

        for tag in soup.find_all(["a", "h1", "h2", "h3", "p"]):
            text = clean(tag.get_text(" ", strip=True))

            if len(text) < 12 or len(text) > 180:
                continue

            if not any(a in text for a in GOOD_AREAS):
                continue

            if has_old_date(text):
                continue

            if any(w in text for w in BLUE_WORDS):
                blue.append(text)
                continue

            if any(w in text for w in BAIT_WORDS):
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
    print("TOKENある？", bool(LINE_TOKEN))

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
    print("起動:", VERSION)
    blue, bait = extract()
    print("青物件数:", len(blue))
    print("ベイト件数:", len(bait))

    msg = make_report(blue, bait)
    print(msg)
    send(msg)

if __name__ == "__main__":
    main()
