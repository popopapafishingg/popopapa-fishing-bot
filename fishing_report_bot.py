import os
import requests
from bs4 import BeautifulSoup
import time

VERSION = "ALLSPOT_ROBUST_20260429"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
LINE_TOKEN = os.environ.get("POPO_LINE_TOKEN")


# =========================
# 共通: HTTPラッパー
# =========================

def fetch_html(url: str) -> str | None:
    """
    HTMLを取得する。失敗したら None を返して続行する。
    """
    try:
        print(f"[INFO] Fetching {url}")
        res = requests.get(url, timeout=15)
        print(f"[INFO] Fetched {url} -> status {res.status_code}")
        if res.status_code != 200:
            print(f"[WARN] {url} status {res.status_code}, skip.")
            return None
        res.encoding = res.apparent_encoding
        return res.text
    except Exception as e:
        print(f"[WARN] fetch_html 失敗: {url} error={e}")
        return None


# =========================
# 各サイトごとのざっくり抽出
# =========================

KEYWORDS_BASE = [
    "釣果", "青物", "ブリ", "メジロ", "ハマチ",
    "サゴシ", "サワラ", "イワシ", "アジ", "サバ", "ベイト"
]


def _generic_extract(html: str, name: str) -> list[str]:
    """
    共通ロジック: 釣果っぽいテキストブロックをざっくり拾う。
    """
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    texts: list[str] = []

    for tag in soup.find_all(["article", "li", "div", "section"]):
        text = tag.get_text(separator=" ", strip=True)
        if not text:
            continue

        if any(k in text for k in KEYWORDS_BASE):
            texts.append(f"[{name}] {text}")

    return texts


def extract_from_marunishi(html: str) -> list[str]:
    return _generic_extract(html, "丸西")


def extract_from_fishingmax(html: str) -> list[str]:
    return _generic_extract(html, "FMAX")


def extract_from_suiken(html: str) -> list[str]:
    return _generic_extract(html, "水軒渡船")


def extract_from_kishiwada(html: str) -> list[str]:
    return _generic_extract(html, "岸和田渡船")


def extract_from_mukogawa(html: str) -> list[str]:
    return _generic_extract(html, "武庫川渡船")


def extract_from_yume(html: str) -> list[str]:
    return _generic_extract(html, "夢フィッシング")


def extract_from_izumisano(html: str) -> list[str]:
    return _generic_extract(html, "泉佐野一文字")


# =========================
# 集計: 青物 / ベイト
# =========================

BLUE_KEYWORDS = [
    "青物", "ブリ", "メジロ", "ハマチ",
    "サゴシ", "サワラ", "メジロクラス", "ブリクラス"
]
BAIT_KEYWORDS = [
    "イワシ", "アジ", "サバ", "豆アジ", "小アジ", "ベイト", "小魚"
]


def extract() -> tuple[list[str], list[str]]:
    """
    7サイトから釣果テキストを集めて、青物／ベイトのヒット行を返す。
    """
    all_texts: list[str] = []

    # 丸西
    html = fetch_html("https://f-marunishi.com/fishing/fishingcat/sea")
    if html:
        try:
            all_texts.extend(extract_from_marunishi(html))
        except Exception as e:
            print(f"[WARN] 丸西抽出失敗: {e}")

    # フィッシングマックス
    html = fetch_html("https://fishingmax.co.jp/")
    if html:
        try:
            all_texts.extend(extract_from_fishingmax(html))
        except Exception as e:
            print(f"[WARN] FMAX抽出失敗: {e}")

    # 水軒渡船
    html = fetch_html("http://wakayama-suikentosen.com/tiyouka.html")
    if html:
        try:
            all_texts.extend(extract_from_suiken(html))
        except Exception as e:
            print(f"[WARN] 水軒抽出失敗: {e}")

    # 岸和田渡船
    html = fetch_html("http://kishiwadatosen.com/result/")
    if html:
        try:
            all_texts.extend(extract_from_kishiwada(html))
        except Exception as e:
            print(f"[WARN] 岸和田抽出失敗: {e}")

    # 武庫川渡船
    html = fetch_html("https://www.amagyo.com/choukax.php")
    if html:
        try:
            all_texts.extend(extract_from_mukogawa(html))
        except Exception as e:
            print(f"[WARN] 武庫川抽出失敗: {e}")

    # 夢フィッシング
    html = fetch_html("http://blog.livedoor.jp/yumefishing/")
    if html:
        try:
            all_texts.extend(extract_from_yume(html))
        except Exception as e:
            print(f"[WARN] 夢フィッシング抽出失敗: {e}")

    # 泉佐野一文字
    html = fetch_html("https://ameblo.jp/izumisanoitimonji/")
    if html:
        try:
            all_texts.extend(extract_from_izumisano(html))
        except Exception as e:
            print(f"[WARN] 泉佐野抽出失敗: {e}")

    blue_hits: list[str] = []
    bait_hits: list[str] = []

    for t in all_texts:
        if any(k in t for k in BLUE_KEYWORDS):
            blue_hits.append(t)
        if any(k in t for k in BAIT_KEYWORDS):
            bait_hits.append(t)

    print(f"[INFO] 青物件数: {len(blue_hits)}")
    print(f"[INFO] ベイト件数: {len(bait_hits)}")

    return blue_hits, bait_hits


# =========================
# OpenAI まわり
# =========================

def ask_chatgpt(prompt: str) -> str:
    """
    ChatGPTにプロンプトを投げて、テキストを返す。
    失敗したら例外を上に投げる。
    """
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
        "temperature": 0.6,
    }

    res = requests.post(url, json=data, headers=headers, timeout=40)
    print(f"[INFO] OpenAI API status: {res.status_code}")
    res.raise_for_status()
    j = res.json()
    return j["choices"][0]["message"]["content"]


def make_draft_report(blue: list[str], bait: list[str]) -> str:
    """
    最初のレポート案を作る（AIに丸投げ）。
    """
    blue_count = len(blue)
    bait_count = len(bait)
    blue_sample = "\n".join(blue[:3])
    bait_sample = "\n".join(bait[:3])

    prompt = f"""
あなたはポポパパ専属の釣果アドバイザーAIです。

ポポパパの行動範囲に近い次の釣り場から、青物とベイトの気配をざっくり集計しました。

対象エリア:
- 丸西（南港方面）
- フィッシングマックス（阪神間）
- 水軒渡船
- 岸和田渡船
- 武庫川渡船
- 夢フィッシング（尼崎方面）
- 泉佐野一文字

集計結果:
- 青物に関する釣果情報のヒット件数: {blue_count} 件
- ベイト（イワシ・アジ・サバなど）に関するヒット件数: {bait_count} 件

青物ヒット例（最大3件まで抜粋）:
{blue_sample}

ベイトヒット例（最大3件まで抜粋）:
{bait_sample}

これらの情報から、次のことを行ってください。

1. 今日の青物の「総合評価」を、10点満点で1点刻みでつけてください。
2. 「ショア青物狙いのポポパパ」向けに、
   - 今日の雰囲気（良さそうか、渋そうか）
   - 期待できる時間帯や潮のイメージ
   - ポイント選びのざっくりした考え方（テトラ帯、沖向き、内向き、一文字、沖堤など）
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


def refine_report_if_needed(draft: str) -> str:
    """
    テンプレからズレていないか自己チェックさせて、
    必要ならAI自身にテンプレどおりに書き直させる。
    """
    try:
        prompt = f"""
あなたは「釣果アドバイザーAIポポパパ」のレポート整形係です。

以下は、あなたがポポパパに向けて出したドラフトレポートです。

----- ドラフトレポート -----
{draft}
----- ここまで -----

このレポートが、次のテンプレートどおりになっているか確認してください。

テンプレート:
- 1行目に「総合評価: X/10点」（Xは1〜10の整数）
- その下に、空行を1行あける
- そのあとに4つ前後の短い文章（1〜3行ずつ）で、
  - 今日の雰囲気
  - 期待できる時間帯や潮のイメージ
  - ポイント選びのざっくりした考え方
  - 行く／行かないを決めやすくする一言
  をシンプルに説明する

もしドラフトがこのテンプレートから外れている場合は、
あなた自身でテンプレートどおりの形に整えてから出力してください。

出力は、
「整形済みレポート本文だけ」
にしてください。
"""
        fixed = ask_chatgpt(prompt)
        return fixed.strip()
    except Exception as e:
        print(f"[WARN] refine_report_if_needed 失敗: {e}")
        return draft


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
# LINE送信
# =========================

def send(msg: str):
    """
    LINE Notify へ送信する。失敗してもクラッシュさせない。
    """
    if not LINE_TOKEN:
        print("LINE トークンが設定されていません。標準出力のみ行います。")
        print(msg)
        return

    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"message": msg}

    try:
        res = requests.post(url, headers=headers, data=data, timeout=15)
        print(f"[INFO] LINE Notify status: {res.status_code}")
        res.raise_for_status()
        print("[INFO] LINE 送信成功")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] LINE 送信に失敗しました: {e}")
        print("----- 本来送る予定だったメッセージ -----")
        print(msg)
        print("----- ここまで -----")


# =========================
# メイン
# =========================

def main():
    print("起動:", VERSION)

    blue, bait = extract()

    # レポートドラフト
    try:
        draft = make_draft_report(blue, bait)
    except Exception as e:
        print(f"[WARN] ChatGPTドラフト生成に失敗: {e}")
        draft = (
            "ポポパパ釣果AI 簡易レポート\n"
            f"青物ヒット件数: {len(blue)}\n"
            f"ベイトヒット件数: {len(bait)}\n"
            "※AIレポート生成に失敗したため、件数のみのお知らせです。"
        )

    # テンプレ自己修正
    final_report = refine_report_if_needed(draft)

    print("----- 最終レポート（LINE送信予定） -----")
    print(final_report)
    print("----- ここまで -----")

    # 自己評価
    try:
        self_review_prompt = build_self_review_prompt(final_report)
        self_review = ask_chatgpt(self_review_prompt)
    except Exception as e:
        print(f"[WARN] 自己評価の生成に失敗: {e}")
        self_review = "自己評価の生成に失敗しました。"

    full_message = f"[ポポパパ釣果AI]\n{VERSION}\n\n{final_report}\n\n――――――――――\n自己評価メモ\n{self_review}"

    print("----- LINEに送る最終メッセージ -----")
    print(full_message)
    print("----- ここまで -----")

    send(full_message)


if __name__ == "__main__":
    main()
