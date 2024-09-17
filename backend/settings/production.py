from .base import *
import os
import yaml

DEBUG = False
ALLOWED_HOSTS = ['wlm-uk.toolforge.org']  # Update this with your Toolforge domain

# Load configuration from toolforge.yaml
with open('/data/project/wlm-uk/toolforge.yaml', 'r') as f:
    tf_config = yaml.safe_load(f)

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': tf_config['DB_NAME'],
        'USER': tf_config['DB_USER'],
        'PASSWORD': tf_config['DB_PASSWORD'],
        'HOST': tf_config['DB_HOST'],
        'PORT': tf_config['DB_PORT'],
    }
}

# Production-specific settings
SECURE_SSL_REDIRECT = False  # Toolforge handles HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

STATIC_ROOT = '/data/project/wlm-uk/www/static'
STATIC_URL = '/static/'

MEDIA_ROOT = '/data/project/wlm-uk/www/media'
MEDIA_URL = '/media/'

# Use WhiteNoise for serving static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'