FROM python:3.10-slim-buster

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y build-essential

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5003

# Start the application
# CMD ["./docker-entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:5003", "app:app"]