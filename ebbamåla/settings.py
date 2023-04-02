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
        'fontawesome_6',
        'django_activeurl',
        'imagekit',
        'markdownx',
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
        'website.middleware.LoginRequiredMiddleware'
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

    DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


class Development(Common):
    DEBUG = True
    ALLOWED_HOSTS = []
    MEDIA_ROOT = os.path.join(Common.BASE_DIR, 'media')
    SECRET_KEY = 'decafbad'
    DS_API_KEY = 'decafbad'
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s - %(name)s.%(funcName)s:%(lineno)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
                'level': 'DEBUG',
            }
        },
        'root': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }


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
        'formatters': {
            'verbose': {
                'format': '%(levelname)s - %(name)s.%(funcName)s:%(lineno)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
                'level': 'INFO',
            },
            'syslog': {
                'class': 'logging.handlers.SysLogHandler',
                'formatter': 'verbose',
                'address': '/dev/log',
                'level': 'INFO',
            },
            'mail_admins': {
                'class': 'django.utils.log.AdminEmailHandler',
                'level': 'ERROR',
            }
        },
        'root': {
            'handlers': ['console', 'syslog', 'mail_admins'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
