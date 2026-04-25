FROM mcr.microsoft.com/playwright/python:v1.52.0-noble

WORKDIR /app

COPY requirements.txt .

# ① 先にライブラリ入れる
RUN pip install -r requirements.txt

# ② そのあとPlaywright
RUN playwright install --with-deps

COPY . .

CMD ["python", "fishing_report_bot.py"]
