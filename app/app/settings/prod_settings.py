import os
from .base_settings import *

DEBUG = False

ALLOWED_HOSTS = []

LOGGING_LEVEL = os.getenv('LOGGING_LEVEL_PROD', 'WARNING')

# modify to suit your needs:
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
