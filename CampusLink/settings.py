import os
from pathlib import Path
import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = ['localhost','127.0.0.1','.onrender.com']
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'MyLogin',   
    'Myapp',     
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'Myapp.middleware.auto_logout.AutoLogoutMiddleware',

]

ROOT_URLCONF = 'CampusLink.urls'

# --- TEMPLATES ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Allow Django to detect templates in all app folders + optional global "templates" folder
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'CampusLink.wsgi.application'

# --- DATABASE CONFIG ---
DATABASES = {
    "default": dj_database_url.parse(config("DATABASE_URL")),
}
DATABASES['default']['CONN_MAX_AGE'] = config("DB_CONN_MAX_AGE", default=60, cast=int)


# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- STATIC FILES CONFIG ---
STATIC_URL = '/static/'

# Tell Django where to collect static files from (for `collectstatic`)
STATICFILES_DIRS = [
    BASE_DIR / "Myapp" / "static",  # Path to your Myapp/static folder
]

# When running collectstatic (for deployment), files will be copied here
STATIC_ROOT = BASE_DIR / "staticfiles"

# --- DEFAULT PRIMARY KEY FIELD TYPE ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ✅ Auto logout configuration (5 minutes)
AUTO_LOGOUT_DELAY = 300  # seconds

# Optional (recommended for safety)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
