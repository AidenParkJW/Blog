from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["blog.anzinda.com"]

# debug toolbar
INTERNAL_IPS = [
    #"127.0.0.1",
]

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': PROPERTIES["database"]["name"],
        'HOST': PROPERTIES["database"]["host"],
        'PORT': PROPERTIES["database"]["port"],
        'USER': PROPERTIES["database"]["user"],
        'PASSWORD': PROPERTIES["database"]["password"],
        'OPTIONS': {
            'driver': 'SQL Server Native Client 11.0',
            'MARS_Connection': True,
            'driver_supports_utf8': True,
        }
    }
}

WSGI_APPLICATION = "Blog.wsgi.wsgi_prd.application"