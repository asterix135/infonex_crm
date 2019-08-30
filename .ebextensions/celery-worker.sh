#!/usr/bin/env bash

# Get django environment variables
celeryenv=`cat /opt/python/current/env | tr '\n' ',' | sed 's/export //g' | sed 's/$PATH/%(ENV_PATH)s/g' | sed 's/$PYTHONPATH//g' | sed 's/$LD_LIBRARY_PATH//g'`
celeryenv=${celeryenv%?}

# Create celery configuraiton script
celeryconf="[program:celeryd-worker]
; Set full path to celery program if using virtualenv
command=/opt/python/run/venv/bin/celery worker -A PROJECT_NAME -P solo --loglevel=INFO -n worker.%%h

directory=/opt/python/current/app/enq_web
user=nobody
numprocs=1
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker.log
autostart=true
autorestart=true
startsecs=10

; Need to wait for currently executing tasks to finish at shutdown.
; Increase this if you have very long running tasks.
stopwaitsecs = 600

; When resorting to send SIGKILL to the program to terminate it
; send SIGKILL to its whole process group instead,
; taking care of its children as well.
killasgroup=true

; if rabbitmq is supervised, set its priority higher
; so it starts first
priority=998

environment=$celeryenv
"

# Create the celery supervisord conf script
echo "$celeryconf" | tee /opt/python/etc/celery.conf

# Add configuration script to supervisord conf (if not there already)
if ! grep -Fxq "[include]" /opt/python/etc/supervisord.conf
  then
  echo "[include]" | tee -a /opt/python/etc/supervisord.conf
  echo "files: celery.conf" | tee -a /opt/python/etc/supervisord.conf
fi

# Reread the supervisord config
/usr/local/bin/supervisorctl -c /opt/python/etc/supervisord.conf reread

# Update supervisord in cache without restarting all services
/usr/local/bin/supervisorctl -c /opt/python/etc/supervisord.conf update

# Start/Restart celeryd through supervisord
/usr/local/bin/supervisorctl -c /opt/python/etc/supervisord.conf restart celeryd-worker
