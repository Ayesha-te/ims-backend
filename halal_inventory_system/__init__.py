# Django project initialization
from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery is not required for basic functionality
    pass

__version__ = "1.0.0"