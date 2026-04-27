import requests
import os
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

VERSION = "FINAL_STRICT_20260427_0235"
LINE_TOKEN = os.getenv("POPO_LINE_TOKEN")

URLS = [
    "https://f-marunishi.com/fishing/fishingcat/sea",
    "https://fishingmax.co.jp/fishingpost/",
]

BLUE_WORDS = [
    "サゴシ", "サワラ", "ブリ", "メジロ", "ハマチ", "ツバス"
]

BAIT_WORDS = [
    "アジ", "マアジ", "サバ", "イワシ", "カタクチ", "コノシロ", "サヨリ", "ベイト"
]

GOOD_AREAS = [
    "貝塚", "貝塚人工島", "和歌山", "マリーナ", "マリーナシティ",
    "田ノ浦", "雑賀崎", "紀ノ川", "水軒", "加太", "衣奈", "中紀"
]

BAD_WORDS = [
    "釣果情報", "海釣り 釣果情報", "川釣り 釣果情報",
    "ノマセ釣果", "マリーナシティにてノマセ釣果",
    "入荷", "商品", "お知らせ", "セール", "イベント", "営業時間",
    "スタッフ募集", "アジング・メバリング", "ロックフィッシュ",
    "南芦屋浜", "須磨", "六甲", "船", "ボート", "沖", "イカダ",
    "チャレ", "・・・", "...", "お持ち込み","スタッフ釣行",
    "アジュール","舞子","神戸空港","親水護岸",
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
        print("FETCH ERROR:", url, e)
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
    # 2026/04/03 みたいな日付があれば、今日・昨日以外は古い扱い
    dates = re.findall(r"20\d{2}/\d{2}/\d{2}", text)
    if not dates:
        return False

    today = datetime.now()
    ok_dates = {
        today.strftime("%Y/%m/%d"),
        (today - timedelta(days=1)).strftime("%Y/%m/%d"),
    }

    for d in dates:
        if d not in ok_dates:
            return True

    return False

def extract():
    blue = []
    bait = []

    for url in URLS:
        html = fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all(["a", "h1", "h2", "h3", "p"]):
            text = clean(tag.get_text(" ", strip=True))

            if len(text) < 10 or len(text) > 180:
                continue

            if any(bad in text for bad in BAD_WORDS):
                continue

            if has_old_date(text):
                continue

            area = any(a in text for a in GOOD_AREAS)
            is_blue = any(w in text for w in BLUE_WORDS)
            is_bait = any(w in text for w in BAIT_WORDS)

            # 青物は「魚名あり」だけ。本物の魚名が無いノマセ・釣果は拾わない。
            if is_blue and area:
                blue.append(text)
                continue

            # ベイトは空っぽ回避用
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
参考ベイトあり

{body}

結論：
完全無風ではないけど青物は弱い
ブリやで（まだ遠い）"""

    return f"""【ポポパパ釣果AI】
{VERSION}
更新：{now}

青物気配なし
参考ベイトも薄い

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
    blue, bait = extract()
    print("VERSION:", VERSION)
    print("青物:", blue)
    print("ベイト:", bait)
    msg = make_report(blue, bait)
    print(msg)
    send(msg)

if __name__ == "__main__":
    main()
