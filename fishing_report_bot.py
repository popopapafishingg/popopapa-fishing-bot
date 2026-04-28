import os
import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

VERSION = "POPOPAPA_TOSEN_FINAL_20260428"

LINE_TOKEN = os.getenv("POPO_LINE_TOKEN")

URLS = [
    # 店系
    "https://f-marunishi.com/fishing/fishingcat/sea",
    "https://fishingmax.co.jp/fishingpost/",

    # 渡船・現場系
    "http://wakayama-suikentosen.com/tiyouka.html",
    "http://kishiwadatosen.com/result/",
    "https://www.amagyo.com/choukax.php",
    "http://blog.livedoor.jp/yumefishing/",
    "https://ameblo.jp/izumisanoitimonji/",
]

BLUE_WORDS = ["ブリ","メジロ","ハマチ","ツバス","サゴシ","サワラ"]
BAIT_WORDS = ["アジ","サバ","イワシ","カタクチ","サヨリ","ベイト"]

GOOD_AREAS = [
    "和歌山","貝塚","岸和田","泉佐野","泉南",
    "マリーナ","水軒","紀ノ川","田ノ浦","雑賀崎"
]

BAD_WORDS = [
    "入荷","商品","お知らせ","セール","イベント",
    "スタッフ","募集","営業時間"
]

# -----------------------------

def fetch(url):
    try:
        return requests.get(url, timeout=15).text
    except:
        return ""

def clean(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def has_old_date(text):
    today = datetime.now()
    dates = re.findall(r"(\d{4})/(\d{1,2})/(\d{1,2})", text)

    for y,m,d in dates:
        try:
            dt = datetime(int(y),int(m),int(d))
            if today - dt > timedelta(days=2):
                return True
        except:
            pass
    return False

def uniq(lst):
    res = []
    for x in lst:
        if x not in res:
            res.append(x)
    return res

def short(t):
    return t[:40] + "…" if len(t) > 40 else t

# -----------------------------

def extract():
    blue = []
    bait = []

    for url in URLS:
        html = fetch(url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        # 渡船系は全文拾う
        if any(x in url for x in ["tos", "chouka", "livedoor", "ameblo"]):
            texts = [soup.get_text(" ", strip=True)]
        else:
            texts = [t.get_text(" ", strip=True) for t in soup.find_all(["a","h1","h2","p"])]

        for raw in texts:
            text = clean(raw)

            if len(text) < 12:
                continue

            if any(b in text for b in BAD_WORDS):
                continue

            if has_old_date(text):
                continue

            area = any(a in text for a in GOOD_AREAS)
            is_blue = any(w in text for w in BLUE_WORDS)
            is_bait = any(w in text for w in BAIT_WORDS)

            # 青物（最優先）
            if is_blue and area:
                blue.append(text)
                continue

            # ベイト（広く）
            if is_bait:
                bait.append(text)

    return uniq(blue)[:3], uniq(bait)[:3]

# -----------------------------

def make_msg(blue, bait):
    now = datetime.now().strftime("%m/%d %H:%M")

    if blue:
        return f"""ポポパパ釣果AI
更新：{now}
青物：気配あり🔥
注目：{short(blue[0])}
判断：朝マズメ勝負
ブリやで🔥"""

    if bait:
        return f"""ポポパパ釣果AI
更新：{now}
青物：なし
ベイト：{short(bait[0])}
判断：様子見〜ワンチャン
ブリやで（まだ遠い）"""

    return f"""ポポパパ釣果AI
更新：{now}
青物：なし
ベイト：薄い
判断：今日は様子見
ブリやで（来てへん）"""

# -----------------------------

def send(msg):
    if not LINE_TOKEN:
        print("LINE_TOKEN無し")
        print(msg)
        return

    try:
        res = requests.post(
            "https://api.line.me/v2/bot/message/broadcast",
            headers={
                "Authorization": f"Bearer {LINE_TOKEN}",
                "Content-Type": "application/json",
            },
            json={"messages":[{"type":"text","text":msg[:4000]}]},
            timeout=20,
        )
        print("送信:", res.status_code)
    except Exception as e:
        print("送信エラー:", e)
        print(msg)

# -----------------------------

def main():
    print("起動:", VERSION)

    blue, bait = extract()

    print("青物:", len(blue))
    print("ベイト:", len(bait))

    msg = make_msg(blue, bait)

    print(msg)

    send(msg)

# -----------------------------

if __name__ == "__main__":
    main()
