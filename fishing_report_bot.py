import os
import json
import requests

# ==== 環境変数 ====
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
LINE_TOKEN = os.environ.get("POPO_LINE_TOKEN")

VERSION = "ALLSPOT_ROBUST_20260429"

SYSTEM_PROMPT = """
あなたは釣果情報を要約するAIです。

絶対に守るルール:
- 最大5行以内にまとめる
- 各行は20〜40文字程度
- 説明は最小限だけ書く
- 箇条書き（- ・ 1. など）は使わない
- 釣りに行くか迷っている人向けに、結論をはっきり書く
"""


# ==== OpenAI呼び出し ====
def ask_chatgpt(system_prompt: str, user_prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",  # 実際に使っているモデル名に合わせてOK
        "messages": [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
        "temperature": 0.5,
    }

    try:
        print("[INFO] OpenAI API 呼び出し開始")
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        print("[INFO] OpenAI API status:", res.status_code)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("[ERROR] OpenAI 失敗:", e)
        return "AIレポート生成に失敗しました。"


def make_draft_report(summary_text: str) -> str:
    user_prompt = f"""
以下が、今日の青物とベイトの集計結果です。

{summary_text}

この情報をもとに、釣りに行くべきかどうかをコメントしてください。
"""
    return ask_chatgpt(SYSTEM_PROMPT, user_prompt)


def make_self_review(final_report: str) -> str:
    self_review_prompt = f"""
次のレポートを自分で簡単に振り返ってください。

{final_report}

最大2行で、
「良かった点」と「次に直したい点」を一言ずつ書いてください。
"""
    return ask_chatgpt(
        "あなたは自分の文章を短く振り返るAIです。短く率直に書きます。",
        self_review_prompt,
    )


# ==== あなたの send 関数（ここが実際に届いていた形） ====
def send(msg: str):
    try:
        url = "https://api.line.me/v2/bot/message/broadcast"
        headers = {
            "Authorization": f"Bearer {LINE_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "messages": [
                {
                    "type": "text",
                    "text": msg
                }
            ]
        }

        res = requests.post(url, headers=headers, json=payload, timeout=30)
        print("LINE送信結果:", res.status_code, res.text)

    except Exception as e:
        print("LINE送信失敗:", e)
        print(msg)


# ==== メイン処理（ここに釣果集計を差し込む） ====
def main():
    # 本当はここでスクレイピングして summary_text を作る
    # いまはテスト用に仮の値
    summary_text = "青物ヒット件数: 61\nベイトヒット件数: 128"

    draft = make_draft_report(summary_text)
    self_review = make_self_review(draft)

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

    send(full_message)


if __name__ == "__main__":
    main()
