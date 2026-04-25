print("🔥 最新コード動いてる 🔥")
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

LINE_TOKEN = "IAYqlIVl9Jh6RcvZ5C+YpHmPUv7B7uxLAU89NPSakzeS/25hb/VWjM70OvmihycYxE/C1ssd0nmdTDMTNQzlu6R6NQ95k5ccLZCuFyc19eAh1Gdx8W+hBjezZa0GdKrf+Ej+TIEaYYOd4qQBohYddQdB04t89/1O/w1cDnyilFU="

USER_ID = "Uf7e227607853d00dc5b4d9614f4761ab"

URL = "https://fishingmax.co.jp/fishingpost/"

def fetch_page():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers, timeout=20)
    r.raise_for_status()
    return r.text

def extract_hits():
    blue_hits = []
    sub_hits = []

    html = fetch_page()
    soup = BeautifulSoup(html, "html.parser")

    articles = soup.select("h3")

    for a in articles:
        text = a.get_text(strip=True)

        if len(text) < 10:
            continue

        # 🔥 青物
        if any(word in text for word in [
            "サゴシ", "サワラ", "ブリ", "メジロ", "ハマチ", "ツバス"
        ]):
            blue_hits.append(text)
            continue

        # 🔸 サブ釣果（保険）
        if any(word in text for word in [
            "アジ", "サバ", "チヌ", "イカ"
        ]):
            sub_hits.append(text)

    # 優先：青物 → 無ければサブ
    hits = blue_hits if blue_hits else sub_hits

    # 重複削除
    clean = []
    for h in hits:
        if h not in clean:
            clean.append(h)

    return clean[:5]

def judge_report(hits):
    return "🔥 新版テスト成功 🔥"
更新：{now}

釣果情報なし

結論：
今日は完全に様子見や
ブリやで（来てへん）"""

    body = "\n".join([f"・{h}" for h in hits])

    score = 20
    blue_flag = False

    for h in hits:
        if any(word in h for word in ["サゴシ", "サワラ"]):
            score += 40
            blue_flag = True

        if any(word in h for word in ["ブリ", "メジロ", "ハマチ", "ツバス"]):
            score += 40
            blue_flag = True

    if score >= 80:
        mode = "爆釣🔥"
        conclusion = "今すぐ行け"
    elif score >= 60:
        mode = "チャンス"
        conclusion = "ワンチャンあり"
    else:
        mode = "渋い"
        conclusion = "青物厳しい"

    return f"""【ポポパパ釣果AI】
更新：{now}

モード：{mode}
スコア：{score}

直近気配：
{body}

結論：
{conclusion}

一言：
{"ブリやで🔥" if blue_flag else "ブリやで（気配なし）"}"""

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
