FROM python:3.11-slim

WORKDIR /app

RUN pip install requests beautifulsoup4

COPY . .

CMD ["python", "fishing_report_bot.py"]
