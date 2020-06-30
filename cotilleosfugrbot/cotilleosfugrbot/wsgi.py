"""
WSGI config for cotilleosfugrbot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import threading
import logging
from time import sleep
import atexit

from webhook_tools import register, unregister

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cotilleosfugrbot.settings')

# Initialization code

logger = logging.getLogger(__name__)

def regfunc():
    sleep(3)
    id = register()
    logger.info(f"Aplicación registrada en Twitter con id: {id}")

t = threading.Thread(target=regfunc)
t.start()

# Clean-up code

def exitfunc():
    unregister()
    logger.info("Aplicación desuscrita de la feed de Twitter")

atexit.register(exitfunc)

application = get_wsgi_application()
