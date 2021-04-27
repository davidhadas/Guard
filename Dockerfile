FROM python:3.8.8-slim
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY ./src /app/src
COPY ./gunicorn.sh /app
WORKDIR /app
ENTRYPOINT ["./gunicorn.sh"]
