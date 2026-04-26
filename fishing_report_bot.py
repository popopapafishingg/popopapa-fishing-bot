import requests
import os
from bs4 import BeautifulSoup

LINE_TOKEN = os.getenv("POPO_LINE_TOKEN")

URL = "https://f-marunishi.com/fishing/fishingcat/sea"

def fetch():
    try:
        r = requests.get(URL, timeout=10)
        return r.text
    except:
        return ""

def main():
    print("デバッグ開始")

    html = fetch()
    print("HTML長さ:", len(html))

    soup = BeautifulSoup(html, "html.parser")

    count = 0

    for tag in soup.find_all(["a","h1","h2","h3","p"]):
        text = tag.get_text(strip=True)

        if len(text) < 10:
            continue

        print("TEXT:", text)
        count += 1

        if count > 20:
            break

    print("取得件数:", count)

if __name__ == "__main__":
    main()
