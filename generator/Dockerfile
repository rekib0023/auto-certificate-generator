FROM python:3.10-slim-buster

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y build-essential
RUN apt-get install -y wkhtmltopdf python3-dev default-libmysqlclient-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV WKHTMLTOPDF_PATH=/usr/bin/wkhtmltopdf

# Make the script executable
RUN chmod +x init.sh

# Start the application
CMD ["./init.sh"]