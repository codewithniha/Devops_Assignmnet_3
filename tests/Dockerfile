# Custom test image: Python + Chrome + ChromeDriver + Selenium
FROM python:3.11-slim

# Install system deps + Chrome
RUN apt-get update && apt-get install -y \
    wget curl gnupg unzip \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install matching ChromeDriver
RUN CHROME_VER=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+') && \
    CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VER}/linux64/chromedriver-linux64.zip" && \
    wget -q "$CHROMEDRIVER_URL" -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver*

WORKDIR /tests

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p test-results

CMD ["pytest", "-v", "--html=test-results/report.html", "--self-contained-html"]
