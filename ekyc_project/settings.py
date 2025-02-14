"""
Django settings for ekyc_project project.

Generated by 'django-admin startproject' using Django 4.2.17.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

is_envfile = False
env_file = [".env.local", ".env.prod", ".env.dev", ".env"]
for file in env_file:
    if os.path.isfile(os.path.join(BASE_DIR, file)):
        is_envfile = True
        load_dotenv(os.path.join(BASE_DIR, file))
        break

if not os.path.exists(os.path.join(BASE_DIR, "logs", "console.log")):
    with open("console.log", "w") as f:
        f.close()



LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",  # Capture all levels of logs (DEBUG and above)
            "class": "logging.StreamHandler",  # Write logs to the console
            #"filename": os.path.join(BASE_DIR, "console.log"),  # Log file path
            "formatter": "standard",  # Format logs for simplicity
        },
        "output": {
            "level": "DEBUG", #caputure all levels of logs (DEBUG and above)
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "output.log"),
            "maxBytes": 50000,
            "backupCount": 2,
            "formatter": "simple",
        }
    },
    "formatters": {
        "standard": {
            "format": "%(message)s",  # Simple output format
        },
        "simple": {
            "format": "%(asctime)s - %(levelname)s -> %(message)s",  # Simple output format
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],  # Redirect Django logs to the file handler
            "level": "DEBUG",  # Capture DEBUG and above
            "propagate": True,  # Prevent duplicate logging
        },
        "django.server": {
            "handlers": ["console"],  # Redirect server-related logs (e.g., HTTP requests)
            "level": "DEBUG",  # Capture INFO and above
            "propagate": True,
        },
        "ekyc": {
            "handlers": ["console", "output"],
            "level": "INFO",
        }
    },
    "root": {
        "handlers": ["console"],  # Capture all logs from the root logger
        "level": "DEBUG",
        "propagate": True,
    },
}
    


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY") 
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get("DEBUG", 1))

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    #my apps
    "ekyc",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    #user defined middleware
    "ekyc_project.middleware.new_middleware"
]

ROOT_URLCONF = "ekyc_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR, 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ekyc_project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT"),
    }
}

#Email setup
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("E_USER")
EMAIL_HOST_PASSWORD = os.environ.get("E_PSWD")
SERVER_EMAIL = EMAIL_HOST_USER
#EMAIL_FROM = os.environ.get("E_FROM")


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"
#STATIC_ROOT = os.path.join(BASE_DIR, 'static_cdn')
STATICFILES_DIR = [
    os.path.join(BASE_DIR, "static"),
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#custom user model
AUTH_USER_MODEL = "ekyc.CustomUser"

#setup the authentication backend attributes for username to email kinda stuff.
# AUTHENTICATION_BACKENDS = [
#     "ekyc.backends.EmailBackend", 
#     "django.contrib.auth.backends.ModelBackend",
# ]

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/ekyc_home/"

# AUTHENTICATION_BACKENDS = [
#     "django.contrib.auth.backends.ModelBackend",
#     "ekyc.auth_backend.EmailBackend",
# ]
