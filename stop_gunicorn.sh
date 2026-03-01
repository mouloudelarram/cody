#!/bin/bash
PIDFILE="gunicorn.pid"

if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    echo "Stopping Gunicorn with PID $PID"
    kill "$PID"
    rm "$PIDFILE"
else
    echo "PID file not found. Is Gunicorn running?"
fi
