#!/bin/bash
# gunicorn main:app \
#     --workers 4 \
#     --worker-class uvicorn.workers.UvicornWorker \
#     --bind 0.0.0.0:80 \
#     --reload \
#     --max-requests 50 \
#     --max-requests-jitter 10 \
#     --access-logfile access.log \
#     --error-logfile error.log

gunicorn --config gunicorn_conf.py app:app
# gunicorn -c gunicorn_conf.py app:app --worker-class uvicorn.workers.UvicornWorker --preload
