import os
import json
import requests

# ========= 環境変数 =========
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
LINE_TOKEN = os.environ.get("POPO_LINE_TOKEN")

VERSION = "ALLSPOT_ROBUST_20260429"

# ========= OpenAI用プロンプト =========
SYSTEM_PROMPT = """
あなたは釣果情報を要約するAIです。

絶対に守るルール:
- 最大5行以内にまとめる
- 各行は20〜40文字程度
- 説明は最小限だけ書く
- 箇条書き（- ・ 1. など）は使わない
- 釣りに行くか迷っている人向けに、結論をはっきり書く
"""


# ========= OpenAI呼び出し =========
def ask_chatgpt(system_prompt: str, user_prompt: str) -> str:
    if not OPENAI_API_KEY:
        print("[WARN] OPENAI_API_KEY が設定されていません。")
        return "AIレポート生成に失敗しました。"

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",  # ここは使っているモデル名に合わせて変更
        "messages": [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
        "temperature": 0.5,
    }

    try:
        print("[INFO] OpenAI API 呼び出し開始")
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"[INFO] OpenAI API status: {res.status_code}")
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[ERROR] OpenAI への問い合わせに失敗しました: {e}")
        return "AIレポート生成に失敗しました。"


# ========= レポート生成 =========
def make_draft_report(summary_text: str) -> str:
    """
    summary_text には「青物〇件、ベイト〇件」などの集計結果を入れる。
    """
    user_prompt = f"""
以下が、今日の青物とベイトの集計結果です。

{summary_text}

この情報をもとに、釣りに行くべきかどうかをコメントしてください。
"""
    return ask_chatgpt(SYSTEM_PROMPT, user_prompt)


def make_self_review(final_report: str) -> str:
    """
    レポートの自己評価を短く生成する。
    """
    self_review_prompt = f"""
次のレポートを、自分で簡単に振り返ってください。


{final_report}

最大2行で、
「良かった点」と「次に直したい点」を一言ずつ教えてください。
"""
    return ask_chatgpt(
        "あなたは自分の文章を短く振り返るAIです。短く率直に書きます。", self_review_prompt
    )


# ========= LINE送信（Messaging API Broadcast） =========
def send(msg: str):
    """
    LINE Messaging API のブロードキャストで送信する。
    エラーが出てもプロセスは落とさず、メッセージはログに残す。
    """
    if not LINE_TOKEN:
        print("[WARN] LINE トークンが設定されていません。標準出力のみ行います。")
        print("----- LINEメッセージ（トークン未設定） -----")
        print(msg)
        print("----- ここまで -----")
        return

    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json",
    }
    body = {
        "messages": [
            {
                "type": "text",
                "text": msg,
            }
        ]
    }

    try:
        print("[INFO] LINE Broadcast 送信開始")
        res = requests.post(url, headers=headers, data=json.dumps(body), timeout=15)
        print(f"[INFO] LINE Broadcast status: {res.status_code}")
        res.raise_for_status()
        print("[INFO] LINE 送信成功")
    except requests.exceptions.HTTPError as e:
        if res.status_code == 429:
            print("[WARN] LINEのレート制限(429)に達しました。しばらく時間をおいてから試してください。")
        else:
            print(f"[ERROR] LINE 送信に失敗しました(HTTP): {e}")
        print("----- 本来送る予定だったメッセージ（保存用） -----")
        print(msg)
        print("----- ここまで -----")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] LINE 送信に失敗しました: {e}")
        print("----- 本来送る予定だったメッセージ（保存用） -----")
        print(msg)
        print("----- ここまで -----")


# ========= メイン処理の例 =========
def main():
    # ここは本来はスクレイピング結果から作る部分。
    # いまは「とりあえず動作確認用」に仮のサマリ文字列を置いています。
    summary_text = "青物ヒット件数: 61\nベイトヒット件数: 128"

    # AIレポート生成
    draft = make_draft_report(summary_text)

    # 自己評価
    self_review = make_self_review(draft)

    # 最終メッセージ組み立て
    full_message = (
        f"[ポポパ釣果AI]\n"
        f"{VERSION}\n\n"
        f"{summary_text}\n\n"
        f"{draft}\n\n"
        f"――――――――――\n"
        f"自己評価メモ\n"
        f"{self_review}"
    )

    print("----- LINEに送る最終メッセージ -----")
    print(full_message)
    print("----- ここまで -----")

    # LINE 送信
    send(full_message)


if __name__ == "__main__":
    main()
