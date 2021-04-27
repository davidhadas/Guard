FROM python:3.8.8-slim
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY ./CF/cf /app/CF/cf
COPY ./*.py /app
COPY ./gunicorn.sh /app
WORKDIR /app
ENTRYPOINT ["./gunicorn.sh"]
