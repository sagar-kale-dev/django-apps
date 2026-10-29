from .common import *

DEBUG = True

SECRET_KEY = 'django-insecure-5+9(qi=ve5pot7khc$m5k9kaz#*wrla9y77lyez@5*kb6sh-r9'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ecommerce",
        "USER": "myuser",
        "PASSWORD": "myuser",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
