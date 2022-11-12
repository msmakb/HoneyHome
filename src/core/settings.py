from main.constants import CRON_AT, CRON_DIR, LOGGERS, PAGES
from django.utils import timezone
from pathlib import Path
import os
import sys


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-o^u2=mwf6*m_1&u=!s8ut6qtvseir*9o0&ua0j&6b)=5bqn1yf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [

    # Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Honey Home System Apps
    'main.apps.MainConfig',
    'human_resources.apps.HumanResourcesConfig',
    'warehouse_admin.apps.WarehouseAdminConfig',
    'social_media_manager.apps.SocialMediaManagerConfig',
    'accounting_manager.apps.AccountingManagerConfig',
    'distributor.apps.DistributorConfig',
    'ceo.apps.CEOConfig',

    # 3rd Party Apps
    'django_filters',
    'django_crontab',
]

MIDDLEWARE = [

    # django Middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Honey Home System Middleware
    'main.middleware.AllowedClientMiddleware',
    'main.middleware.LoginRequiredMiddleware',
    'main.middleware.AllowedUserMiddleware',
]

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = False


# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

EXCLUDED_PAGES_FORM_REQUIRED_AUTHENTICATION = [
    PAGES.INDEX,
    PAGES.LOGOUT,
    PAGES.ABOUT_PAGE,
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crontab jobs
CRONJOBS = [
    (CRON_AT.EVERY_HOUR, CRON_DIR.MAIN + '.setMagicNumber'),
    (CRON_AT.EVERY_MINUTE, CRON_DIR.HUMAN_RESOURCES + '.checkTaskDateTime'),
    (CRON_AT.FIRST_MINUTE_ON_SUNDAY, CRON_DIR.HUMAN_RESOURCES + '.addWeekToRate'),
]

LOGS_PATH = BASE_DIR.parent / 'logs'

Path(LOGS_PATH).mkdir(parents=True, exist_ok=True)
LOG_FILE_NAME = str(timezone.datetime.date(timezone.now())) + '_HoneyHome.log'
LOGGING_LEVEL = 'DEBUG' if DEBUG else 'INFO'
HANDLERS = ['console', 'file']
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "{asctime} [{levelname}] - {name}.{module}.('{funcName}') - {message}",
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.__stdout__,
            'formatter': 'simple',
        },
        'file': {
            'level': LOGGING_LEVEL,
            'class': 'logging.FileHandler',
            'filename': LOGS_PATH / LOG_FILE_NAME,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        "django": {
            'handlers': HANDLERS,
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        "django.server": {
            'handlers': HANDLERS,
            'level': os.getenv('DJANGO_LOG_LEVEL', LOGGING_LEVEL),
            'filters': ['require_debug_true'],
            'propagate': False,
        },
        "django.template": {
            'handlers': HANDLERS,
            'level': os.getenv('DJANGO_LOG_LEVEL', LOGGING_LEVEL),
            'filters': ['require_debug_true'],
            'propagate': False,
        },
        "django.db.backends.schema": {
            'handlers': HANDLERS,
            'level': os.getenv('DJANGO_LOG_LEVEL', LOGGING_LEVEL),
            'filters': ['require_debug_true'],
            'propagate': False,
        },
        "django.security.*": {
            'handlers': HANDLERS,
            'level': os.getenv('DJANGO_LOG_LEVEL', LOGGING_LEVEL),
            'filters': ['require_debug_true'],
            'propagate': False,
        },
        LOGGERS.MIDDLEWARE: {
            'handlers': HANDLERS,
            'level': 'WARNING',
            'propagate': False,
        },
        LOGGERS.MAIN: {
            'handlers': HANDLERS,
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
        LOGGERS.HUMAN_RESOURCES: {
            'handlers': HANDLERS,
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
    },
}
