#!/bin/sh
#gunicorn --chdir Guard Guard:app -w 1 -b 0.0.0.0:8080  --worker-class=gevent --worker-connections=1000
gunicorn   --chdir Guard Main:app -w 1 -b 0.0.0.0:8080  --worker-class=gevent --worker-connections=1000
#--threads=2 --worker-class=gthread
