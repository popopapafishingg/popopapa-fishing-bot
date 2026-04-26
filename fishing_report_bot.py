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

# 🎯 青物（広めに拾う）
BLUE_WORDS = [
    "サゴシ","サワラ","ブリ","メジロ","ハマチ","ツバス",
    "ナブラ","入れ食い","青物",
    "ノマセ","飲ませ","泳がせ","ヒット"
]

# 🎯 ベイト
BAIT_WORDS = [
    "アジ","マアジ","サバ","イワシ","カタクチ","コノシロ","サヨリ","ベイト"
]

# 🎯 対象エリア
GOOD_AREAS = [
    "貝塚","貝塚人工島","和歌山","マリーナ","田ノ浦",
    "雑賀崎","紀ノ川","水軒","加太","衣奈","中紀"
]

# ❌ 完全排除（見出し・広告・関係ない場所）
BAD_WORDS = [
    "入荷","商品","お知らせ","セール","イベント","営業時間",
    "スタッフ募集","アジング・メバリング","ロックフィッシュ",
    "南芦屋浜","須磨","六甲","船","ボート","沖","イカダ",
    "チャレ","・・・","...",
    "釣果情報","海釣り 釣果情報","川釣り 釣果情報"
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

def extract():
    blue = []
    bait_good = []
    bait_any = []

    for url in URLS:
        html = fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all(["a","h1","h2","h3","p"]):
            text = clean(tag.get_text(" ", strip=True))

            if len(text) < 10 or len(text) > 160:
                continue

            if any(bad in text for bad in BAD_WORDS):
                continue

            # 🎯 内容があるものだけ残す
            if not any(w in text for w in BLUE_WORDS + BAIT_WORDS):
                continue

            area = any(a in text for a in GOOD_AREAS)
            is_blue = any(w in text for w in BLUE_WORDS)
            is_bait = any(w in text for w in BAIT_WORDS)

            # 🔥 青物最優先
            if is_blue:
                blue.append(text)
                continue

            # 🎯 ベイト（エリア内）
            if is_bait and area:
                bait_good.append(text)
                continue

            # 🛟 空回避用
            if is_bait:
                bait_any.append(text)

    # 🔥 最新順だけ使用
    blue = uniq(blue)[:3]
    bait_good = uniq(bait_good)[:3]
    bait_any = uniq(bait_any)[:2]

    return blue, bait_good, bait_any

def make_report(blue, bait_good, bait_any):
    now = datetime.now().strftime("%m/%d %H:%M")

    if blue:
        body = "\n".join([f"・{short(x)}" for x in blue])
        return f"""【ポポパパ釣果AI】
更新：{now}

🔥青物気配あり🔥

{body}

結論：
朝マズメ勝負
ブリやで🔥"""

    if bait_good:
        body = "\n".join([f"・{short(x)}" for x in bait_good])
        return f"""【ポポパパ釣果AI】
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
更新：{now}

青物気配：なし
参考ベイトあり

{body}

結論：
完全無風ではない
ブリやで（まだ遠い）"""

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
    blue, bait_good, bait_any = extract()
    msg = make_report(blue, bait_good, bait_any)
    print(msg)
    send(msg)

if __name__ == "__main__":
    main()
