import os


workers = os.environ.get('GUNICORN_NUM_WORKERS', 6)
max_requests = os.environ.get('GUNICORN_MAX_REQUESTS', 0)
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'gevent')
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
timeout = 20
accesslog = '-'
errorlog = '-'
access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
