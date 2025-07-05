bind = "0.0.0.0:8000"
workers = 3
worker_class = "sync"
threads = 2
timeout = 120
keepalive = 120

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
django_settings = "health_project.settings"
chdir = str(BASE_DIR)

# Graceful shutdown timeout
graceful_timeout = 30

# Server name
server_name = "health_project"

# Windows-specific settings
daemon = False
pidfile = "gunicorn.pid"
