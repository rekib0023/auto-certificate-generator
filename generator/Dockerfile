FROM python:3.10-slim-buster

RUN apt-get update && \
    apt-get install -y wkhtmltopdf && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV WKHTMLTOPDF_PATH=/usr/bin/wkhtmltopdf

CMD flask run --host=0.0.0.0 --debug