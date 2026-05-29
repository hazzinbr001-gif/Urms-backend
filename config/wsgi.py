"""
WSGI config for config project.
"""

import os

from django.core.wsgi import get_wsgi_application

# Default to production settings — overridden locally via env or manage.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_production")

application = get_wsgi_application()
