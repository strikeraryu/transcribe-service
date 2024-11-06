# gunicorn.conf.py
import multiprocessing

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = 2
worker_class = 'sync'
worker_connections = 1000
timeout = 300
keepalive = 2

# Process naming
proc_name = 'gunicorn_flask_app'

# Logging
accesslog = '-'  # stdout
errorlog = '-'   # stderr
loglevel = 'debug'


# Maximum request size (adjust according to your needs)
limit_request_line = 0
limit_request_fields = 100
limit_request_field_size = 0  # unlimited
