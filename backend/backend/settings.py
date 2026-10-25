import os
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured('Set DJANGO_SECRET_KEY in production.')
    SECRET_KEY = 'django-insecure-unimart-dev-key-change-me'
EMAIL_VERIFICATION_REQUIRED = os.environ.get(
    'EMAIL_VERIFICATION_REQUIRED',
    'false' if DEBUG else 'true',
).lower() == 'true'
ALLOWED_HOSTS = [host.strip() for host in os.environ.get(
    'DJANGO_ALLOWED_HOSTS',
    'localhost,127.0.0.1,.vercel.app',
).split(',') if host.strip()]
vercel_url = os.environ.get('VERCEL_URL')
if vercel_url:
    ALLOWED_HOSTS.append(vercel_url.removeprefix('https://').removeprefix('http://').split('/')[0])
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'https://*.vercel.app',
).split(',') if origin.strip()]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'marketplace',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.parent / 'html'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'
ASGI_APPLICATION = 'backend.asgi.application'

database_url = os.environ.get('DATABASE_URL')
if database_url:
    parsed_database_url = urlparse(database_url)
    database_options = parse_qs(parsed_database_url.query)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': unquote(parsed_database_url.path.lstrip('/')),
            'USER': unquote(parsed_database_url.username or ''),
            'PASSWORD': unquote(parsed_database_url.password or ''),
            'HOST': parsed_database_url.hostname,
            'PORT': parsed_database_url.port or '5432',
            'OPTIONS': {
                'sslmode': database_options.get('sslmode', ['require'])[0],
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'unimart_db'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR.parent / 'css',
    BASE_DIR.parent / 'js',
]
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
