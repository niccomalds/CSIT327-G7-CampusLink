import os
from pathlib import Path
import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent


if os.environ.get("RENDER", "") != "true":
    # Local development - use python-decouple
    SECRET_KEY = config('SECRET_KEY')
    DEBUG = config("DEBUG", default=False, cast=bool)
    ALLOWED_HOSTS = ['localhost','127.0.0.1','.onrender.com']
    CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']
    
    # Local database configuration
    DATABASES = {
        "default": dj_database_url.parse(config("DATABASE_URL")),
    }
    DATABASES['default']['CONN_MAX_AGE'] = config("DB_CONN_MAX_AGE", default=60, cast=int)
else:
    # Render production - use environment variables
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'unsafe-dev-key')
    DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'
    
    # Parse from environment variables 
    allowed_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts.split(',') if h.strip()]
    
    csrf_origins = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '')
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in csrf_origins.split(',') if o.strip()]
    
    # Production database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }

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
    'whitenoise.middleware.WhiteNoiseMiddleware',  
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
STATICFILES_DIRS = [
    BASE_DIR / "Myapp" / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise configuration 
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Security settings for production 
if os.environ.get('RENDER'):
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# --- DEFAULT PRIMARY KEY FIELD TYPE ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ✅ Auto logout configuration (5 minutes)
AUTO_LOGOUT_DELAY = 300  # seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LOGIN_REDIRECT_URL = '/Myapp/dashboard/'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

