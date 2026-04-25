import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

LINE_TOKEN = "IAYqlIVl9Jh6RcvZ5C+YpHmPUv7B7uxLAU89NPSakzeS/25hb/VWjM70OvmihycYxE/C1ssd0nmdTDMTNQzlu6R6NQ95k5ccLZCuFyc19eAh1Gdx8W+hBjezZa0GdKrf+Ej+TIEaYYOd4qQBohYddQdB04t89/1O/w1cDnyilFU="

USER_ID = "Uf7e227607853d00dc5b4d9614f4761ab"

TARGET_AREAS = [
    "和歌山マリーナシティ", "貝塚人工島", "田ノ浦", "雑賀崎",
    "紀ノ川", "水軒", "煙樹ヶ浜", "樽井", "りんくう"
]

TARGET_FISH = [
    "ブリ", "メジロ", "ハマチ", "ツバス",
    "サワラ", "サゴシ",
    "アジ", "デカアジ",
    "ヒラメ", "マゴチ",
    "ヒラスズキ", "アオリイカ", "イカ"
]

URLS = [
    "https://fishingmax.co.jp/fishingpost/",
    "https://anglers.jp/",
    "https://fishing.ne.jp/fishingpost/",
]

def fetch_page(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print("FETCH ERROR:", url, e)
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
]

    CATCH_WORDS = [
        "釣れ", "釣果", "ヒット", "キャッチ", "本", "匹", "杯",
        "cm", "㎝", "センチ", "朝", "夕", "ルアー", "ジグ",
        "バイブ", "セットアッパー", "飲ませ", "泳がせ"
    ]

    for url in URLS:
        html = fetch_page(url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text("\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        for line in lines:
            if "リアルタイム" in line or "情報" in line or "・・・" in line or "…" in line or "..." in line:
    continue
            if len(line) < 8 or len(line) > 160:
                continue

            if any(ng in line for ng in NG_WORDS):
                continue

            area_hit = any(area in line for area in TARGET_AREAS)
            fish_hit = any(fish in line for fish in TARGET_FISH)
            catch_hit = any(word in line for word in CATCH_WORDS)

            # 魚種＋釣果っぽい言葉、または場所＋釣果っぽい言葉だけ拾う
            if catch_hit and (area_hit or fish_hit):
    # 数字入り優先（本物の釣果）
    if any(char.isdigit() for char in line):
        hits.insert(0, line)  # 上に持ってくる
    else:
        hits.append(line)
    clean = []
    for h in hits:
        if h not in clean:
            clean.append(h)

    return clean[:15]

def judge_report(hits):
    today = datetime.now().strftime("%m/%d %H:%M")

    if not hits:
        return f"""【ポポパパ釣果AI】
更新：{today}

対象：大阪〜和歌山ショア

直近釣果：
目立つ情報なし

判定：
今日は情報少なめ。
無理せず様子見推奨。

ルアー候補：
1位 ジグ
2位 バイブ
3位 セットアッパー

結論：
釣れたらブリやで。
釣れへんかったら通常運転やで。"""

    body = "\n".join([f"・{h}" for h in hits])

    score = 40
    if any(("サゴシ" in h or "サワラ" in h) for h in hits):
        score += 25
    if any(("ブリ" in h or "メジロ" in h or "ハマチ" in h) for h in hits):
        score += 25
    if any(("和歌山マリーナシティ" in h or "貝塚人工島" in h) for h in hits):
        score += 10

    if score >= 80:
        mode = "熱い"
        conclusion = "行く価値あり。朝マズメ勝負。"
    elif score >= 60:
        mode = "普通"
        conclusion = "ワンチャンあり。無理ない範囲で。"
    else:
        mode = "渋い"
        conclusion = "様子見寄り。釣れたら事件。"

    return f"""【ポポパパ釣果AI】
更新：{today}

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
ブリやで。たぶんアジやけど。"""

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
    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)
    r.raise_for_status()

def main():
    hits = extract_hits()
    report = judge_report(hits)
    send_line(report)
    print("DONE")

if __name__ == "__main__":
    main()
