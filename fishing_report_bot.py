import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

LINE_TOKEN = "IAYqlIVl9Jh6RcvZ5C+YpHmPUv7B7uxLAU89NPSakzeS/25hb/VWjM70OvmihycYxE/C1ssd0nmdTDMTNQzlu6R6NQ95k5ccLZCuFyc19eAh1Gdx8W+hBjezZa0GdKrf+Ej+TIEaYYOd4qQBohYddQdB04t89/1O/w1cDnyilFU="

USER_ID = "Uf7e227607853d00dc5b4d9614f4761ab"

URLS = [
    "https://fishingmax.co.jp/fishingpost/",
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

    soup = BeautifulSoup(fetch_page(URLS[0]), "html.parser")
    text = soup.get_text("\n")

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:

        # 🔥 ナブラ系は無条件採用
        if any(word in line for word in ["ナブラ", "なぶら", "入れ食い"]):
            hits.insert(0, line)
            continue

        # 青物だけ拾う
        if any(fish in line for fish in ["メジロ", "ブリ", "ハマチ", "ツバス", "サゴシ", "サワラ"]):
            if "釣れ" in line or "ヒット" in line:
                hits.insert(0, line)
                continue

    # 重複削除
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

        if any(word in h for word in ["サゴシ", "サワラ"]):
            score += 40
            blue_flag = True

        if any(word in h for word in ["ブリ", "メジロ", "ハマチ", "ツバス"]):
            score += 40
            blue_flag = True

        if "ナブラ" in h or "なぶら" in h:
            score += 50
            nabl_flag = True
            blue_flag = True

        if "入れ食い" in h:
            score += 30
            blue_flag = True

    if score > 100:
        score = 100

    if score >= 80:
        mode = "爆釣🔥"
        conclusion = "今すぐ行け"
    elif score >= 60:
        mode = "チャンス"
        conclusion = "ワンチャンあり"
    else:
        mode = "渋い"
        conclusion = "様子見"

    return f"""【ポポパパ釣果AI】
更新：{now}

モード：{mode}
スコア：{score}

直近気配：
{body}

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

    requests.post(url, headers=headers, json=data)

def main():
    hits = extract_hits()
    report = judge_report(hits)
    send_line(report)

if __name__ == "__main__":
    if os.getenv("RUN_MODE") == "cron":
        main()
    else:
        print("起動のみ（送信しない）")
