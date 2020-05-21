from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["blog.daonelab.com", "blog.home.daonelab.com"]

# debug toolbar
INTERNAL_IPS = [
    #"127.0.0.1",
]

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': PROPERTIES["database"]["name"],
        'HOST': PROPERTIES["database"]["host"],
        'PORT': PROPERTIES["database"]["port"],
        'USER': PROPERTIES["database"]["user"],
        'PASSWORD': PROPERTIES["database"]["password"],
    }
}

WSGI_APPLICATION = "Blog.wsgi.wsgi_prd.application"