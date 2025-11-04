# Gunicorn configuration file
pythonbind = "0.0.0.0:8000"
workers = 2
threads = 2
timeout = 60
worker_class = "sync"
accesslog = "-"
errorlog = "-"
loglevel = "info"