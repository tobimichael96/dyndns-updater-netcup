FROM python:3.9-alpine

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .
COPY src/ .

RUN pip install -r requirements.txt

CMD ["python", "/app/main.py"]