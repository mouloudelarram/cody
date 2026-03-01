#!/bin/bash
# run_gunicorn.sh
# Navigate to your app directory

# File to store PID
PIDFILE="gunicorn.pid"

# Run gunicorn in the background
nohup gunicorn -w 4 -b 127.0.0.1:5000 app:app > gunicorn.log 2>&1 &

# Save the PID
echo $! > "$PIDFILE"
echo "Gunicorn started in the background with PID $(cat $PIDFILE)"
