import requests
from bs4 import BeautifulSoup
from datetime import datetime
from playwright.sync_api import sync_playwright

LINE_TOKEN = "IAYqlIVl9Jh6RcvZ5C+YpHmPUv7B7uxLAU89NPSakzeS/25hb/VWjM70OvmihycYxE/C1ssd0nmdTDMTNQzlu6R6NQ95k5ccLZCuFyc19eAh1Gdx8W+hBjezZa0GdKrf+Ej+TIEaYYOd4qQBohYddQdB04t89/1O/w1cDnyilFU="

USER_ID = "Uf7e227607853d00dc5b4d9614f4761ab"

URL = "https://anglers.jp/areas/1309/fishes/932/catches"

def fetch():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)

        html = page.content()
        browser.close()
        return html

def extract():
    html = fetch()
    soup = BeautifulSoup(html, "html.parser")

    hits = []

    for t in soup.find_all(["div", "span"]):
        text = t.get_text(strip=True)

        if len(text) < 10 or len(text) > 120:
            continue

        if any(word in text for word in [
            "サゴシ", "サワラ", "ブリ", "メジロ", "ハマチ", "ツバス"
        ]):
            hits.append(text)

        if "ナブラ" in text or "入れ食い" in text:
            hits.insert(0, text)

    return list(dict.fromkeys(hits))[:10]

def report(hits):
    now = datetime.now().strftime("%m/%d %H:%M")

    if not hits:
        return f"""【ポポパパ釣果AI】
更新：{now}

青物気配なし
今日は様子見や
ブリやで（来てへん）"""

    body = "\n".join([f"・{h}" for h in hits])

    return f"""【ポポパパ釣果AI】
更新：{now}

直近青物：
{body}

結論：
行く価値あり
ブリやで🔥"""

def send(text):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Authorization": "Bearer " + LINE_TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "messages": [{"type": "text", "text": text}]
    }

    requests.post(url, headers=headers, json=data)

def main():
    hits = extract()
    text = report(hits)
    send(text)

if __name__ == "__main__":
    main()
