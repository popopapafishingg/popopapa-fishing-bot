import os
import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

# バージョン管理用
VERSION = "BALANCE_FINAL_20260428_SELF_REVIEW_v1"

# 環境変数からトークンなど取得
LINE_TOKEN = os.getenv("POPO_LINE_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 監視するサイト
URLS = [
    "https://f-marunishi.com/fishing/fishingcat/sea",
    "https://fishingmax.co.jp/",
]

# キーワード類
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
    "サバ",
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
    "西宮",
    "西宮浜",
]

# 何日前までを「新しい釣果」とみなすか
MAX_DAYS = 2

# 前回レポート保存用ファイル
LAST_REPORT_FILE = "last_report.txt"


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


def has_old_date(text: str) -> bool:
    """
    テキストに含まれる日付が MAX_DAYS より古ければ True を返す。
    日付が取れない場合は False（古いと判定しない）。
    """
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


def uniq(items):
    seen = set()
    result = []
    for x in items:
        if x in seen:
            continue
        seen.add(x)
        result.append(x)
    return result


def extract_from_marunishi(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    texts: list[str] = []

    for article in soup.find_all(["article", "div"], class_=re.compile("post|article|entry|item")):
        text = article.get_text(separator=" ", strip=True)
        if not text:
            continue
        texts.append(text)

    for a in soup.find_all("a"):
        t = a.get_text(separator=" ", strip=True)
        if t and len(t) > 15:
            texts.append(t)

    return texts


def extract_from_fishingmax(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    texts: list[str] = []

    for article in soup.find_all(["article", "div"], class_=re.compile("post|article|entry|item")):
        text = article.get_text(separator=" ", strip=True)
        if not text:
            continue
        texts.append(text)

    for a in soup.find_all("a"):
        t = a.get_text(separator=" ", strip=True)
        if t and len(t) > 15:
            texts.append(t)

    return texts


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
            soup = BeautifulSoup(html, "html.parser")
            texts = [soup.get_text(separator=" ", strip=True)]
            source = "その他"

        for text in texts:
            if not text:
                continue

            if has_old_date(text):
                continue

            is_blue = any(w in text for w in BLUE_WORDS)
            is_bait = any(w in text for w in BAIT_WORDS)
            area = any(a in text for a in GOOD_AREAS)

            if is_blue and area:
                blue.append(f"[{source}] {text}")
                continue

            if is_bait:
                bait.append(f"[{source}] {text}")

    blue = uniq(blue)[:3]
    bait = uniq(bait)[:3]

    return blue, bait


def build_raw_summary(blue: list[str], bait: list[str]) -> str:
    """
    AIに渡すための「材料まとめ」。
    """
    lines: list[str] = []

    lines.append("")
    if not blue:
        lines.append("なし")
    else:
        for i, text in enumerate(blue, start=1):
            lines.append(f"{i}. {text[:300]}")

    lines.append("\n")
    if not bait:
        lines.append("なし")
    else:
        for i, text in enumerate(bait, start=1):
            lines.append(f"{i}. {text[:300]}")

    return "\n".join(lines)


def load_last_report() -> str:
    try:
        if not os.path.exists(LAST_REPORT_FILE):
            return ""
        with open(LAST_REPORT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def save_last_report(text: str):
    try:
        with open(LAST_REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print(f"[WARN] save_last_report failed: {e}")


def build_report_with_chatgpt(summary_text: str, last_report: str) -> str:
    if not OPENAI_API_KEY:
        return "OPENAI_API_KEY が設定されていません。Railway の環境変数を確認してください。"

    url = "https://api.openai.com/v1/chat/completions"

    system_prompt = """
あなたは「ポポパパ釣果AI」の頭脳です。
目的は、毎朝自動で集まる釣果テキストだけから、
ポポパパが「今日は青物を狙って釣りに行くかどうか」を直感的に判断できるLINEメッセージを作ることです。

絶対に守ること:
- サイト本文をそのままコピペしない。必ず要約して短く書く。
- 青物の明確な釣果が無い日は、はっきり「青物の明確な釣果情報なし」と書く。
- 情報が少ない日は、水増しせず「情報が少ない」と正直に書く。
- 分からないことは「不明」と書き、絶対にでっち上げない。
- 人間に「追加で〇〇してください」とお願いしない。手元の情報だけで完結させる。

あなたは、前回のレポートも参考にしながら、
「今回はどれくらい変えるか」を自分で判断し、小さな改善を積み重ねていきます。
自己評価が高いほど前回に近づけ、低いほど思い切って変えてください。
"""

    now = datetime.now()
    updated_at = now.strftime("%m/%d %H:%M")

    user_prompt = f"""
以下が、釣果サイトから抽出したテキストの要約です。

{summary_text}

以下が、前回LINEに送ったレポート全文です。（なければ空です）


{last_report}

これらを踏まえて、次の2つをセットで出力してください。

1. 今回LINEに送るレポート本文
- 全体で10行以内に収めてください。
- 冒頭2行は必ず次のとおりにしてください。
  1行目: ポポパパ釣果AI
  2行目: 更新：{updated_at}
- そのあとに、次の情報を含めてください。
  - 今日の「行く価値」判断（行く価値あり／微妙／やめとこ をあなたの言葉で1行）
  - 青物の有無（明確な釣果が無ければ「青物の明確な釣果情報なし」と1行で書く）
  - ベイトの雰囲気（ざっくり1〜2行）
  - 気になる釣り場があれば1〜2カ所、各1行以内
- サイトの生テキスト・コピペは出さないこと。

レポート本文の最後に、必ず次の1行を付けてください。
「自己評価：10点満点中 X 点。理由：YYYY」
ここでXは0〜10の数字、理由は短く1行で。

2. 次こう直した方がいいメモ（開発者向け）
- 3〜8行程度の日本語で、
  「次はフォーマットや内容をどう変えると良さそうか」
  をあなた自身の視点でメモしてください。
- ここではコードは書かず、日本語だけで構いません。

出力の中では、
- 最初に「」という見出し
- そのあとにレポート本文
- 一行空けてから「」という見出し
- そのあとに改善メモ

という構成にしてください。
"""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-4.1-mini",
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


def send(msg: str):
    if not LINE_TOKEN:
        print("LINE トークンが設定されていません。標準出力のみ行います。")
        print(msg)
        return

    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"message": msg}

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            res = requests.post(url, headers=headers, data=data, timeout=10)
            res.raise_for_status()
            print(f"[INFO] LINE 送信成功 (試行 {attempt} 回目)")
            return
        except Exception as e:
            print(f"[ERROR] LINE 送信失敗 (試行 {attempt} 回目): {e}")
            if attempt < max_retries:
                time.sleep(5)  # 5秒待ってから再トライ
            else:
                print("[ERROR] 再試行回数を超えたため、今回のメッセージ送信をあきらめます。")
                print("----- 送信しようとした内容 -----")
                print(msg)


def main():
    print("起動:", VERSION)

    blue, bait = extract()

    print("青物件数:", len(blue))
    print("ベイト件数:", len(bait))

    summary_text = build_raw_summary(blue, bait)
    last_report = load_last_report()

    msg = build_report_with_chatgpt(summary_text, last_report)

    # 次回用に保存（AIの自己評価・改善メモも含めて）
    save_last_report(msg)

    print(msg)
    send(msg)


if __name__ == "__main__":
    main()
