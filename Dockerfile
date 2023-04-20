FROM python:3.9

RUN apt update && apt install locales -y
RUN sed -i '/de_DE.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LC_ALL de_DE.UTF-8

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .
COPY src/ .

RUN pip install -r requirements.txt

CMD ["python", "/app/main.py"]