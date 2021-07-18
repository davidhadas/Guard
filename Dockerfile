FROM python:3.8.8-slim
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY ./Guard /app/Guard
COPY ./gunicorn.sh /app
COPY ./FrontEnd /app/FrontEnd
WORKDIR /app
ENTRYPOINT ["./gunicorn.sh"]
