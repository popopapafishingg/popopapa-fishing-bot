import os
import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

# バージョン管理用
VERSION = "BALANCE_FINAL_20260427_CHATGPT_AUTO"

# 環境変数からトークンなど取得
LINE_TOKEN = os.getenv("POPO_LINE_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 監視するサイト
URLS = [
    "https://f-marunishi.com/fishing/fishingcat/sea",
    "https://fishingmax.co.jp/",
]

# キーワード類（あなたの元コードの定義があればそちらを優先して書き換えてください）
BLUE_WORDS = [
    "ブリ",
    "メジロ",
    "ハマチ",
    "ツバス",
    "サゴシ",
    "サワラ",
]
BAIT_WORDS = [
    "イワシ",
    "アジ",
    "サッパ",
    "ベイト",
]
GOOD_AREAS = [
    "泉南",
    "和歌山",
    "紀北",
    "岸和田",
    "貝塚",
    "泉大津",
    "神戸",
]

# 何日前までを「新しい釣果」とみなすか
MAX_DAYS = 2


# 共通のHTTP取得
def fetch_html(url: str) -> str | None:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; fishing-bot/1.0)"
        }
        res = requests.get(url, headers=headers, timeout=20)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        return res.text
    except Exception as e:
        print(f"[ERROR] fetch_html failed: {url} {e}")
        return None


# 日付判定用：テキストから日付を抜いて古いものを除外する簡易版
def has_old_date(text: str) -> bool:
    """
    テキストに含まれる日付が MAX_DAYS より古ければ True を返す。
    日付が取れない場合は False（古いと判定しない）。
    """
    # ざっくり「4/27」「2024-04-27」みたいなものを拾う簡易実装
    today = datetime.now()
    patterns = [
        r"(\d{1,2})月(\d{1,2})日",
        r"(\d{1,2})/(\d{1,2})",
        r"(\d{4})-(\d{1,2})-(\d{1,2})",
    ]

    for pat in patterns:
        m = re.search(pat, text)
        if not m:
            continue

        try:
            if len(m.groups()) == 2:
                # 月日だけ
                month = int(m.group(1))
                day = int(m.group(2))
                year = today.year
                d = datetime(year, month, day)
            elif len(m.groups()) == 3:
                year = int(m.group(1))
                month = int(m.group(2))
                day = int(m.group(3))
                d = datetime(year, month, day)
            else:
                continue

            if today - d > timedelta(days=MAX_DAYS):
                return True
        except Exception:
            continue

    return False


# 重複削除
def uniq(items):
    seen = set()
    result = []
    for x in items:
        if x in seen:
            continue
        seen.add(x)
        result.append(x)
    return result


# 各サイトからテキストをざっくり取る（必要に応じて調整）
def extract_from_marunishi(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    texts: list[str] = []

    # 釣果記事のリンクや本文をざっくり抽出（サイト構造に合わせて後で調整）
    for article in soup.find_all(["article", "div"], class_=re.compile("post|article|entry")):
        text = article.get_text(separator=" ", strip=True)
        if not text:
            continue
        texts.append(text)

    # 予備として a タグのテキストも少し拾う
    for a in soup.find_all("a"):
        t = a.get_text(separator=" ", strip=True)
        if t and len(t) > 15:
            texts.append(t)

    return texts


def extract_from_fishingmax(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    texts: list[str] = []

    for article in soup.find_all(["article", "div"], class_=re.compile("post|article|entry")):
        text = article.get_text(separator=" ", strip=True)
        if not text:
            continue
        texts.append(text)

    for a in soup.find_all("a"):
        t = a.get_text(separator=" ", strip=True)
        if t and len(t) > 15:
            texts.append(t)

    return texts


# メインの抽出ロジック：青物／ベイト
def extract():
    blue: list[str] = []
    bait: list[str] = []

    for url in URLS:
        print(f"[INFO] Fetching {url}")
        html = fetch_html(url)
        if not html:
            continue

        if "f-marunishi.com" in url:
            texts = extract_from_marunishi(html)
            source = "マルニシ"
        elif "fishingmax.co.jp" in url:
            texts = extract_from_fishingmax(html)
            source = "フィッシングマックス"
        else:
            # その他のサイトを増やしたとき用
            soup = BeautifulSoup(html, "html.parser")
            texts = [soup.get_text(separator=" ", strip=True)]
            source = "その他"

        for text in texts:
            if not text:
                continue

            # 古い日付はスキップ
            if has_old_date(text):
                continue

            is_blue = any(w in text for w in BLUE_WORDS)
            is_bait = any(w in text for w in BAIT_WORDS)
            area = any(a in text for a in GOOD_AREAS)

            # 青物（エリアありのみ）
            if is_blue and area:
                blue.append(f"[{source}] {text}")
                continue

            # ベイトは広く拾う（エリア関係なし）
            if is_bait:
                bait.append(f"[{source}] {text}")

    blue = uniq(blue)[:3]
    bait = uniq(bait)[:3]

    return blue, bait


# ChatGPT に渡すためのまとめテキスト
def build_raw_summary(blue: list[str], bait: list[str]) -> str:
    lines: list[str] = []

    lines.append("")
    if not blue:
        lines.append("なし")
    else:
        for i, text in enumerate(blue, start=1):
            lines.append(f"{i}. {text[:200]}")

    lines.append("\n")
    if not bait:
        lines.append("なし")
    else:
        for i, text in enumerate(bait, start=1):
            lines.append(f"{i}. {text[:200]}")

    return "\n".join(lines)


# ChatGPT にレポート作成を依頼（自立AIモード）
def build_report_with_chatgpt(summary_text: str) -> str:
    if not OPENAI_API_KEY:
        return "OPENAI_API_KEY が設定されていません。Railway の環境変数を確認してください。"

    url = "https://api.openai.com/v1/chat/completions"

    system_prompt = """
あなたは釣果情報収集エージェントです。
目的は、毎朝自動で集まる「青物候補テキスト」と「ベイト候補テキスト」だけから、
実用的な釣果レポートを作り、人間の手間を減らすことです。

守るべき方針:
- 情報が少ない日は「今日は情報が少ない」とはっきり書くこと。
- 分からないことは「不明」と書き、でっち上げないこと。
- サイト取得の失敗について、人間に追加作業（スクショなど）を要求しないこと。
- レポートの最後に「明日以降ロジックを改善するなら」の一言メモを書くこと。
"""

    user_prompt = f"""
以下は、釣果サイトから抽出した「青物っぽいテキスト」と「ベイトっぽいテキスト」です。
この情報だけをもとに、関西のショア青物（ブリ・メジロ・ハマチ・ツバス・サゴシなど）の傾向をレポートしてください。

出力フォーマット:
1. 今日の青物の状況まとめ（全体像）
2. 釣り場ごとの青物の傾向（分かる範囲で。分からなければ「不明」と書く）
3. ベイトの状況（多い／少ない／不明を釣り場に絡めて簡潔に）
4. サイトからの情報取得状況（「情報が少ない」「青物情報ほぼ無し」などざっくりでよい）
5. 明日以降ロジックを改善するなら（1〜3行のメモ）

抽出テキスト:
{summary_text}
"""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-4.1-mini",  # コストを抑える軽めモデル
        "messages": [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
        "max_tokens": 1200,
        "temperature": 0.3,
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"ChatGPT への問い合わせに失敗しました: {e}"


# LINE 送信用（あなたの元の send ロジックがあれば置き換えてください）
def send(msg: str):
    if not LINE_TOKEN:
        print("LINE トークンが設定されていません。標準出力のみ行います。")
        print(msg)
        return

    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"message": msg}

    try:
        res = requests.post(url, headers=headers, data=data, timeout=10)
        res.raise_for_status()
        print("[INFO] LINE 送信成功")
    except Exception as e:
        print(f"[ERROR] LINE 送信失敗: {e}")
        print(msg)


def main():
    print("起動:", VERSION)

    blue, bait = extract()

    print("青物件数:", len(blue))
    print("ベイト件数:", len(bait))

    summary_text = build_raw_summary(blue, bait)
    msg = build_report_with_chatgpt(summary_text)

    print(msg)
    send(msg)


if __name__ == "__main__":
    main()
