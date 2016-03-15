# -*- coding: utf-8 -*-
import os
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_DIR = os.environ.get('PROSO_DATA_DIR', os.path.join(BASE_DIR, 'data'))
MEDIA_ROOT = os.environ.get('PROSO_MEDIA_DIR', DATA_DIR)
MEDIA_URL = '/media/'

SECRET_KEY = os.getenv('PROSO_SECRET_KEY', 'really secret key')

ON_PRODUCTION = False
ON_STAGING = False

if os.environ.get('PROSO_ON_PRODUCTION', False):
    ON_PRODUCTION = True
if os.environ.get('PROSO_ON_STAGING', False):
    ON_STAGING = True

if ON_PRODUCTION or ON_STAGING:
    DEBUG = False
else:
    DEBUG = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Vít Stanislav', 'slaweet@gmail.com'),
    ('Jan Papoušek', 'jan.papousek@gmail.com'),
)

EMAIL_SUBJECT_PREFIX = '[slepemapy.cz] '

ALLOWED_HOSTS = [
    'slepemapy.cz',
    'new.slepemapy.cz',
    'production.slepemapy.cz',
    'production-new.slepemapy.cz',
    'outlinemaps.org',
    'es.outlinemaps.org',
    'de.outlinemaps.org',
    '.outlinemaps.org',
    '.slepemapy.cz',
    '.staging.slepemapy.cz',
    '.staging.outlinemaps.org',
    '.devel.outlinemaps.org',
]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'flatblocks',
    'lazysignup',
    'proso_common',
    'proso_ab',
    'proso_configab',
    'proso_models',
    'proso_user',
    'proso_feedback',
    'proso_flashcards',
    'social.apps.django_app.default',
    'geography',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'proso_common.middleware.ToolbarMiddleware',
    'proso_common.middleware.ErrorMiddleware',
    'proso_common.models.CommonMiddleware',
    'proso.django.request.RequestMiddleware',
    'proso.django.config.ConfigMiddleware',
    'proso_configab.models.ABConfigMiddleware',
    'proso.django.cache.RequestCacheMiddleware',
    'proso.django.log.RequestLogMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'proso_common.middleware.LanguageInDomainMiddleware',
    'proso_common.middleware.GoogleAuthChangeDomain',
    'proso_common.middleware.AuthAlreadyAssociatedMiddleware',
)

ROOT_URLCONF = 'geography.urls'

WSGI_APPLICATION = 'geography.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
if ON_PRODUCTION or ON_STAGING:
    DATABASES = {
        'default': {
            'ENGINE': os.environ.get('PROSO_DATABASE_ENGINE', 'django.db.backends.postgresql_psycopg2'),
            'OPTIONS': {
                'options': "-c search_path=%s" % os.environ.get('PROSO_DATABASE_SCHEMA', 'public')
            },
            'NAME': os.environ['PROSO_DATABASE_NAME'],
            'USER': os.environ['PROSO_DATABASE_USER'],
            'PASSWORD': os.environ['PROSO_DATABASE_PASSWORD'],
            'HOST': os.environ['PROSO_DATABASE_HOST'],
            'PORT': os.environ['PROSO_DATABASE_PORT'],
        },
    }
else:
    DATABASES = {
        'default': dj_database_url.config(),
    }

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'cs'

LANGUAGES = (
    ('cs', u'Česky'),
    ('de', 'Deutsch'),
    ('en', 'English'),
    ('es', u'Español'),
    ('ru', u'Русский'),
    ('sk', u'Slovensky'),
)

if ON_PRODUCTION:
    LANGUAGE_DOMAINS = {
        'cs': 'slepemapy.cz',
        'sk': 'sk.slepemapy.cz',
        'en': 'outlinemaps.org',
        'es': 'es.outlinemaps.org',
        'de': 'de.outlinemaps.org',
        'ru': 'ru.outlinemaps.org',
    }
    AUTH_DOMAIN = 'slepemapy.cz'
elif ON_STAGING:
    LANGUAGE_DOMAINS = {
        'cs': 'staging.slepemapy.cz',
        'sk': 'sk.staging.slepemapy.cz',
        'en': 'staging.outlinemaps.org',
        'es': 'es.staging.outlinemaps.org',
        'de': 'de.staging.outlinemaps.org',
        'ru': 'ru.staging.outlinemaps.org',
    }
    AUTH_DOMAIN = 'staging.slepemapy.cz'
else:
    LANGUAGE_DOMAINS = {
        'cs': 'localhost:8000',
        'sk': 'sk.localhost:8000',
        'en': 'en.localhost:8000',
        'es': 'es.localhost:8000',
        'de': 'de.localhost:8000',
        'ru': 'ru.localhost:8000',
    }
    AUTH_DOMAIN = 'localhost:8000'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'conf', 'locale'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, '..', 'static')
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'geography', 'static'),
    os.path.join(BASE_DIR, 'proso_mnemonics', 'static'),
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'lazysignup.backends.LazySignupBackend',
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOAuth2',
)

SOCIAL_AUTH_FACEBOOK_KEY = os.getenv('PROSO_FACEBOOK_APP_ID', '')
SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv('PROSO_FACEBOOK_API_SECRET', '')
SOCIAL_AUTH_FACEBOOK_EXTENDED_PERMISSIONS = ['email']

SOCIAL_AUTH_CREATE_USERS = True
SOCIAL_AUTH_FORCE_RANDOM_USERNAME = False
SOCIAL_AUTH_DEFAULT_USERNAME = 'socialauth_user'
LOGIN_ERROR_URL = '/login/error/'
SOCIAL_AUTH_ERROR_KEY = 'socialauth_error'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_SESSION_EXPIRATION = False
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('PROSO_GOOGLE_OAUTH2_CLIENT_ID', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('PROSO_GOOGLE_OAUTH2_CLIENT_SECRET', '')

# http://stackoverflow.com/questions/22005841/is-not-json-serializable-django-social-auth-facebook-login
SESSION_SERIALIZER='django.contrib.sessions.serializers.PickleSerializer'

LOGIN_REDIRECT_URL = '/'

SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'

SOCIAL_AUTH_UID_LENGTH = 222
SOCIAL_AUTH_NONCE_SERVER_URL_LENGTH = 200
SOCIAL_AUTH_ASSOCIATION_SERVER_URL_LENGTH = 135
SOCIAL_AUTH_ASSOCIATION_HANDLE_LENGTH = 125

EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
SERVER_EMAIL = 'info@slepemapy.cz'

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'mail_admins_javascript': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'proso.django.log.AdminJavascriptEmailHandler'
        },
        'request': {
            'level': 'DEBUG',
            'class': 'proso.django.log.RequestHandler',
            'formatter': 'simple'
        },
        'geography_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(DATA_DIR, 'geography.log'),
            'formatter': 'simple',
        }
    },
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s "%(message)s"'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'request', 'mail_admins', 'geography_file'],
            'propagate': True,
            'level': 'DEBUG'
        },
        'javascript': {
            'handlers': ['console', 'mail_admins_javascript', 'geography_file'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.db.backends': {
            'level': 'INFO',
            'handlers': ['console'],
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
}

if ON_PRODUCTION:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
            'TIMEOUT': 60 * 60 * 24 * 7,
            'OPTIONS': {
                'MAX_ENTRIES': 300000,
            },
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': os.path.join(DATA_DIR, '.django_cache'),
            'TIMEOUT': 60 * 60 * 24 * 7,
            'OPTIONS': {
                'MAX_ENTRIES': 30000,
            },
        }
    }

PROSO_CONFIG = {
    'path': os.path.join(BASE_DIR, 'geography', 'proso_config.yaml'),
}
PROSO_FLASHCARDS = {}

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'geography', 'templates'),
)

try:
    from hashes import HASHES
except ImportError:
    HASHES = {}
except SyntaxError:
    HASHES = {}

PROSO_JS_FILES = ['dist/js/bower-libs.js']
