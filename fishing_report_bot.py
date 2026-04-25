import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

LINE_TOKEN = "IAYqlIVl9Jh6RcvZ5C+YpHmPUv7B7uxLAU89NPSakzeS/25hb/VWjM70OvmihycYxE/C1ssd0nmdTDMTNQzlu6R6NQ95k5ccLZCuFyc19eAh1Gdx8W+hBjezZa0GdKrf+Ej+TIEaYYOd4qQBohYddQdB04t89/1O/w1cDnyilFU="

USER_ID = "Uf7e227607853d00dc5b4d9614f4761ab"

URLS = [
    "https://anglers.jp/areas/1309/fishes/932/catches",
    "https://anglers.jp/areas/2306/fishes/932/catches",
    "https://fishingmax.co.jp/fishingpost/",
]

TARGET_AREAS = [
    "和歌山マリーナシティ",
    "マリーナシティ",
    "和歌山市",
    "貝塚人工島",
    "貝塚",
    "田ノ浦",
    "雑賀崎",
    "紀ノ川",
    "水軒",
    "煙樹ヶ浜",
    "樽井",
    "りんくう",

    # 🔥 追加（超重要）
    "加太",
    "衣奈",
    "由良",
    "日高",
    "白浜",
    "御坊",
    "有田",
    "海南",
    "湯浅",
]

TARGET_FISH = [
    "ブリ", "メジロ", "ハマチ", "ツバス",
    "サワラ", "サゴシ",
    "アジ", "ヒラメ", "マゴチ", "ヒラスズキ", "アオリイカ"
]

def fetch_page(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.text
    except:
        return ""

def extract_hits():
    hits = []

    NG_WORDS = [
        "オフショア", "船", "イカダ", "カセ", "釣り方", "ジャンル",
        "アジング", "メバリング", "ロックフィッシュ", "ULSJ", "ＵＬＳＪ",
        "ショアジギング", "イカメタル", "ウキ釣り", "ヤエン",
        "一覧", "カテゴリ", "エリア", "釣果情報", "新着", "人気",
        "リアルタイム", "リアルタイム情報", "情報", "注目", "特集",
        "無料釣り場", "最大級", "近年", "集まっています",
        "・・・", "…", "...",
        "汐見埠頭"
    ]

    CATCH_WORDS = [
        "釣れ", "釣果", "ヒット", "キャッチ", "本", "匹", "杯",
        "cm", "㎝", "センチ", "朝", "夕", "ルアー", "ジグ",
        "バイブ", "セットアッパー", "飲ませ", "泳がせ"
    ]

    SPECIAL_WORDS = [
        "ナブラ", "なぶら", "入れ食い"
    ]

    for url in URLS:
        html = fetch_page(url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text("\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        for line in lines:
            if len(line) < 8 or len(line) > 160:
                continue

            if any(ng in line for ng in NG_WORDS):
                continue

            area_hit = any(area in line for area in TARGET_AREAS)
            fish_hit = any(fish in line for fish in TARGET_FISH)
            catch_hit = any(word in line for word in CATCH_WORDS)
            special_hit = any(word in line for word in SPECIAL_WORDS)

            # 🔥 ナブラ・入れ食いは無条件で拾う
            if special_hit:
                hits.insert(0, line)
                continue

            # 通常判定
            if catch_hit and (area_hit or fish_hit):
                if any(char.isdigit() for char in line):
                    hits.insert(0, line)
                else:
                    hits.append(line)

    clean = []
    for h in hits:
        if h not in clean:
            clean.append(h)

    return clean[:10]

def judge_report(hits):
    now = datetime.now().strftime("%m/%d %H:%M")

    if not hits:
        return f"""【ポポパパ釣果AI】
更新：{now}

青物気配：なし

結論：
今日は無理せん方がええ日やで
ブリやで（来てへん）"""

    body = "\n".join([f"・{h}" for h in hits])

    score = 20
    blue_flag = False
    nabl_flag = False

    for h in hits:

        # 🔥 青物
        if any(word in h for word in ["サゴシ", "サワラ"]):
            score += 50
            blue_flag = True

        if any(word in h for word in ["ブリ", "メジロ", "ハマチ", "ツバス"]):
            score += 50
            blue_flag = True

        # 🔥 ナブラ検出（最強）
        if "ナブラ" in h or "なぶら" in h:
            score += 60
            nabl_flag = True
            blue_flag = True

        # 🔥 入れ食い
        if "入れ食い" in h:
            score += 40
            blue_flag = True

        # 雑魚
        if any(word in h for word in ["アジ", "チヌ", "サバ"]):
            score += 3

    # 上限
    if score > 100:
        score = 100

    if score >= 80:
        mode = "爆釣モード🔥"
        conclusion = "今すぐ行かなあかん"
    elif score >= 60:
        mode = "チャンスあり"
        conclusion = "ワンチャンある"
    else:
        mode = "渋い"
        conclusion = "青物厳しい。様子見"

    return f"""【ポポパパ釣果AI】
更新：{now}

モード：{mode}
スコア：{score}点

直近気配：
{body}

ルアー候補：
1位 ジグ
2位 バイブ
3位 セットアッパー

結論：
{conclusion}

一言：
{"ブリやで🔥" if blue_flag else "ブリやで（気配なし）"}
{"ナブラ出てるぞ🔥" if nabl_flag else ""}"""

def send_line(text):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Authorization": "Bearer " + LINE_TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "messages": [{"type": "text", "text": text[:4500]}],
    }

    r = requests.post(url, headers=headers, json=data, timeout=30)
    print(r.status_code, r.text)

def main():
    hits = extract_hits()
    report = judge_report(hits)
    send_line(report)

if __name__ == "__main__":
    if os.getenv("RUN_MODE") == "cron":
        main()
    else:
        print("起動のみ（送信しない）")
