"""
Django settings for StronaProjektyKol project.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
import json
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(" ")

# Application definition

INSTALLED_APPS = [
    'messaging.apps.MessagesConfig',
    'papers.apps.PapersConfig',
    'users.apps.UsersConfig',
    'documents.apps.DocumentsConfig',
    'django_summernote',
    'django_filters',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'users.middleware.UpdateLastActivityMiddleware'
]

ROOT_URLCONF = 'StronaProjektyKol.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'StronaProjektyKol.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    BASE_DIR / 'app_static',
    BASE_DIR / 'messaging/static/messaging',
    BASE_DIR / 'papers/static/papers',
    BASE_DIR / 'documents/static/documents',
]


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# for crispy forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

SUMMERNOTE_CONFIG = {
    'iframe': True,

    # You can put custom Summernote settings
    'summernote': {
        # As an example, using Summernote Air-mode
        'airMode': False,

        # Change editor size
        'width': '100%',
        'height': '480',

        # https://summernote.org/deep-dive/#custom-toolbar-popover
        'toolbar': [
            ['style', ['style']],
            ['font', ['bold', 'underline', 'clear']],
            ['fontname', ['fontname']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['insert', ['link', 'picture', 'video']],
            ['view', ['fullscreen', 'codeview', 'help']],
        ],

        'lang': 'pl-PL',
        'disable_attachment': True,
    },

}

# #security
X_FRAME_OPTIONS = 'SAMEORIGIN'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 60
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

LOGIN_REDIRECT_URL = 'profile'
LOGIN_URL = 'login'

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "pl-pl")

TIME_ZONE = os.environ.get("TIMEZONE", "Europe/Warsaw")

USE_I18N = True

USE_L10N = True

USE_TZ = True

# EMAIL
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "mail.example.io")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "exmaple")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "example")
EMAIL_PORT = os.environ.get("EMAIL_PORT", "456")
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}

SITE_NAME = os.environ.get("SITE_NAME", "John")
SITE_DOMAIN = os.environ.get("SITE_DOMAIN", "exmple.com")
SITE_ADMIN_MAIL = os.environ.get("SITE_ADMIN_MAIL", "example@example.com")
SITE_ADMIN_PHONE = os.environ.get("SITE_ADMIN_PHONE", "123456789")


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "5ctom(4!o!7+il5ifwlyu77tjwx5q^j=3z^_=wj8rjmvxu_1kf")

ADMINS = [
    ('Admin', os.environ.get("SITE_ADMIN_MAIL", "example@example.com"),)
]
MANAGERS = ADMINS

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(os.environ.get('DEBUG', default='True'))
