import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from decouple import config

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY CONFIG ---
SECRET_KEY = config("SECRET_KEY", default=os.getenv("SECRET_KEY", "insecure-secret-key"))
DEBUG = config("DEBUG", default=(os.getenv("DEBUG") == "True"), cast=bool)

# Allow localhost for local testing, and *.onrender.com for production
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,.onrender.com")
).split(",")


# --- INSTALLED APPS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps
    'MyLogin',
    'Myapp',
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # ✅ WhiteNoise middleware for static file serving on Render
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # ✅ Your custom auto logout middleware
    'Myapp.middleware.auto_logout.AutoLogoutMiddleware',
]

ROOT_URLCONF = 'CampusLink.urls'


# --- TEMPLATES ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # global templates folder
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
# Use PostgreSQL on Render if DATABASE_URL exists, otherwise fallback to local SQLite
if os.getenv("DATABASE_URL"):
    DATABASES = {
        'default': dj_database_url.parse(os.getenv('DATABASE_URL'), conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'  # Optional: Set your timezone
USE_I18N = True
USE_TZ = True


# --- STATIC FILES CONFIG ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "Myapp" / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ✅ WhiteNoise static files optimization
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- SESSION CONFIG ---
AUTO_LOGOUT_DELAY = 300  # seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


# --- DEFAULT PRIMARY KEY FIELD TYPE ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
