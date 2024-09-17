from .base import *
import dj_database_url
from dotenv import load_dotenv

load_dotenv(os.path.join(BASE_DIR, '.env'))

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': dj_database_url.config(default=f'sqlite:///{BASE_DIR}/db.sqlite3', conn_max_age=600)
}

# Development-specific settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'