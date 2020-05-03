from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# debug toolbar
INTERNAL_IPS = [
    #"127.0.0.1",
]

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

WSGI_APPLICATION = "Blog.wsgi.wsgi_dev.application"

# 아래 스크립트가 없어도 logging된다.
# 아래 스크립트는 LOGGING['loggers']에 지정된 logging name을 순회하면서 설정을 바꾸는 기능을 보여준다.
if DEBUG:
    # make all loggers use the console.
    for logger in LOGGING['loggers']:
        #LOGGING['loggers'][logger]['handlers'] = ['console', 'file']
        LOGGING['loggers'][logger]['handlers'] = ['console']

