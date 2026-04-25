FROM mcr.microsoft.com/playwright/python:v1.52.0-noble

WORKDIR /app

RUN pip install requests beautifulsoup4 playwright

RUN python -m playwright install --with-deps

COPY . .

CMD ["python", "fishing_report_bot.py"]
