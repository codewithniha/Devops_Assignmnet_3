FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget curl gnupg unzip \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Use selenium-manager (bundled in selenium 4.6+) — it auto-downloads matching ChromeDriver
WORKDIR /tests
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p test-results

CMD ["pytest", "-v", "--html=test-results/report.html", "--self-contained-html"]
