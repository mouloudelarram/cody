#!/bin/bash

PIDFILE="gunicorn.pid"
LOGFILE="gunicorn.log"

gunicorn -w 4 -b 127.0.0.1:5000 \
    --daemon \
    --pid "$PIDFILE" \
    app:app \
    > "$LOGFILE" 2>&1

