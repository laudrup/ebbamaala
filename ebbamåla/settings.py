"""
Django settings for ebbamåla project.
"""

import os

from configurations import Configuration, values
from django.utils.translation import gettext_lazy as _


class Common(Configuration):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    SECRET_KEY = values.SecretValue()
    DS_API_KEY = values.SecretValue()

    # Application definition
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'bootstrap4',
        'fontawesome',
        'django_activeurl',
        'imagekit',
        'markdownx',
        'django_nose',
        'website',
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'ebbamåla.middleware.LoginRequiredMiddleware'
    ]

    ROOT_URLCONF = 'ebbamåla.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

    WSGI_APPLICATION = 'ebbamåla.wsgi.application'

    # Database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

    # Password validation
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

    # Internationalization
    LANGUAGE_CODE = 'en'
    TIME_ZONE = 'UTC'
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True
    LOCALE_PATHS = [
        os.path.join(BASE_DIR, 'locale'),
    ]
    LANGUAGES = [
        ('en', _('English')),
        ('da', _('Danish')),
        ('pl', _('Polish')),
    ]

    FORMAT_MODULE_PATH = [
        'website.formats',
    ]
    # Static files (CSS, JavaScript, Images)
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]

    MEDIA_URL = '/media/'

    LOGOUT_REDIRECT_URL = '/'
    LOGIN_REDIRECT_URL = '/'

    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

    NOSE_ARGS = [
        '--with-coverage',
        '--cover-package=website',
    ]


class Development(Common):
    DEBUG = True
    ALLOWED_HOSTS = []
    MEDIA_ROOT = os.path.join(Common.BASE_DIR, 'media')


class Production(Common):
    STATIC_ROOT = '/home/www/static'
    MEDIA_ROOT = '/home/www/media'

    ALLOWED_HOSTS = ['xn--ebbamla-ixa.se', 'localhost']
    ADMINS = (
        ('Kasper Laudrup', 'laudrup@stacktrace.dk'),
    )
    EMAIL_HOST = 'localhost'

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler'
            }
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'mail_admins'],
                'propagate': True,
                'level': 'DEBUG',
            },
        }
    }
