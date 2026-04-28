import os
import requests
from bs4 import BeautifulSoup
import time
import re

# バージョン表示用（任意）
VERSION = "BALANCE_STABLE_20260428_v2"

# 環境変数からキーとトークンを取得
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
LINE_TOKEN = os.environ.get("POPO_LINE_TOKEN")


# =========================
#  Webスクレイピング周り
# =========================

def fetch_html(url: str) -> str:
    print(f"[INFO] Fetching {url}")
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    res.encoding = res.apparent_encoding
    return res.text


def extract_from_marunishi(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    texts: list[str] = []

    for article in soup.find_all(["article", "li", "div", "section"]):
        text = article.get_text(separator=" ", strip=True)
        if not text:
            continue

        if any(k in text for k in ["釣果", "青物", "ブリ", "メジロ", "ハマチ", "サゴシ", "サワラ", "イワシ", "アジ", "サバ", "ベイト"]):
            texts.append(text)

    return texts


def extract_from_fishingmax(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    texts: list[str] = []

    for article in soup.find_all(["article", "li", "div", "section"]):
        text = article.get_text(separator=" ", strip=True)
        if not text:
            continue

        if any(k in text for k in ["釣果", "青物", "ブリ", "メジロ", "ハマチ", "サゴシ", "サワラ", "イワシ", "アジ", "サバ", "ベイト"]):
            texts.append(text)

    return texts


def extract() -> tuple[list[str], list[str]]:
    # 丸西
    marunishi_url = "https://f-marunishi.com/fishing/fishingcat/sea"
    marunishi_html = fetch_html(marunishi_url)
    marunishi_texts = extract_from_marunishi(marunishi_html)

    # フィッシングマックス
    fmax_url = "https://fishingmax.co.jp/"
    fmax_html = fetch_html(fmax_url)
    fmax_texts = extract_from_fishingmax(fmax_html)

    all_texts = marunishi_texts + fmax_texts

    blue_keywords = ["青物", "ブリ", "メジロ", "ハマチ", "サゴシ", "サワラ", "メジロクラス", "ブリクラス"]
    bait_keywords = ["イワシ", "アジ", "サバ", "豆アジ", "小アジ", "ベイト", "小魚"]

    blue_hits: list[str] = []
    bait_hits: list[str] = []

    for t in all_texts:
        if any(k in t for k in blue_keywords):
            blue_hits.append(t)
        if any(k in t for k in bait_keywords):
            bait_hits.append(t)

    print(f"[INFO] 青物件数: {len(blue_hits)}")
    print(f"[INFO] ベイト件数: {len(bait_hits)}")

    return blue_hits, bait_hits


# =========================
#  OpenAI まわり
# =========================

def ask_chatgpt(prompt: str) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY が設定されていません。")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "あなたは釣りが大好きな、ポポパパ専属のやさしいアドバイザーAIです。"
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }

    res = requests.post(url, json=data, headers=headers, timeout=30)
    res.raise_for_status()
    j = res.json()
    return j["choices"][0]["message"]["content"]


def make_report(blue: list[str], bait: list[str]) -> str:
    blue_count = len(blue)
    bait_count = len(bait)

    prompt = f"""
あなたはポポパパ専属の釣果アドバイザーAIです。

- 青物に関する釣果情報のヒット件数: {blue_count} 件
- ベイト（イワシ・アジ・サバなど）に関するヒット件数: {bait_count} 件

これらの件数から、次のことを行ってください。

1. 今日の青物の「総合評価」を、10点満点で1点刻みでつけてください。
2. 「ショア青物狙いのポポパパ」向けに、
   - 今日の雰囲気（良さそうか、渋そうか）
   - 期待できる時間帯や潮のイメージ
   - ポイント選びのざっくりした考え方（テトラ帯、沖向き、内向き など）
   を分かりやすく短めにまとめてください。
3. 数字が少ない（もしくはゼロ）場合でも、
   - 「数字が少ない＝絶対釣れない」ではないことを前提に、
   - それでもポポパパが「行く／行かない」を自分で決めやすくなるようなコメントを書いてください。
4. 最後に、明日以降のための一言アドバイスも付けてください。

出力フォーマットは次のようにしてください。


総合評価: X/10点


（ここに短い文章）


（ここに短い文章）


（ここに短い文章）


（ここに短い文章）
"""
    return ask_chatgpt(prompt)


def build_self_review_prompt(report: str) -> str:
    return f"""
あなたは「釣果アドバイザーAIポポパパ」の自己評価係です。

以下は、あなたがポポパパに向けて出した今日の釣果レポートです。

----- ここからレポート -----
{report}
----- ここまでレポート -----

このレポートについて、次の観点で自己評価してください。

1. わかりやすさ（10点満点）
2. 実際の釣行判断に役立つかどうか（10点満点）
3. メンタル面への配慮（プレッシャーをかけすぎていないか）（10点満点）

各項目の点数と、その理由を一言で教えてください。
最後に「次回このレポートを改善するとしたらどこをどう直すか」を具体的に1〜2行で書いてください。

出力フォーマットは次のようにしてください。


わかりやすさ: A/10点
理由: （一言）

実用性: B/10点
理由: （一言）

メンタル配慮: C/10点
理由: （一言）


（ここに1〜2行）
"""


# =========================
#  LINE送信まわり
# =========================

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
        # ここが今まで問題になっていた行：
        # res.raise_for_status() をそのまま呼ぶと例外で落ちるので try の中に置く
        res.raise_for_status()
        print("[INFO] LINE 送信成功")
    except requests.exceptions.RequestException as e:
        # ここで例外をキャッチしてログを出し、スクリプトを落とさない
        print(f"[ERROR] LINE 送信に失敗しました: {e}")
        print("----- 本来送る予定だったメッセージ -----")
        print(msg)
        print("----- ここまで -----")


# =========================
#  エントリポイント
# =========================

def main():
    print("起動:", VERSION)

    blue, bait = extract()

    # メインのレポート生成
    msg = make_report(blue, bait)
    print("----- 生成されたレポート -----")
    print(msg)
    print("----- ここまで -----")

    # 自己評価も1回だけ追加で生成
    try:
        self_review_prompt = build_self_review_prompt(msg)
        self_review = ask_chatgpt(self_review_prompt)
    except Exception as e:
        print(f"[WARN] 自己評価の生成に失敗しました: {e}")
        self_review = "自己評価の生成に失敗しました。"

    full_message = f"{msg}\n\n――――――――――\n自己評価メモ\n{self_review}"

    print("----- LINEに送る最終メッセージ -----")
    print(full_message)
    print("----- ここまで -----")

    send(full_message)


if __name__ == "__main__":
    main()
