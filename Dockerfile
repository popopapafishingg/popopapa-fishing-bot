FROM mcr.microsoft.com/playwright/python:v1.52.0-noble

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

# 👇 ここが修正ポイント
RUN python -m playwright install --with-deps

COPY . .

CMD ["python", "fishing_report_bot.py"]
# test
