import os
from .base_settings import *

DEBUG = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = ['*']

LOGGING_LEVEL = os.getenv('LOGGING_LEVEL_DEV', 'DEBUG')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOGGING_LEVEL,
    },
}
