FROM mcr.microsoft.com/playwright/python:v1.52.0-noble

WORKDIR /app

# 🔥 直接インストール（これが最強）
RUN pip install requests beautifulsoup4 playwright

# 🔥 Playwrightブラウザ入れる
RUN python -m playwright install --with-deps

COPY . .

CMD ["python", "fishing_report_bot.py"]
