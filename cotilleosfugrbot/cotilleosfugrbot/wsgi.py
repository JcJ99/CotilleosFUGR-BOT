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
from webhook_tools import register, unregister, set_welcome_message, remove_welcome_message, put
from chatbot.config import AUTO_REGISTER
from apscheduler.schedulers.background import BackgroundScheduler

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cotilleosfugrbot.settings')
    
# Initialization code

if AUTO_REGISTER:

    logger = logging.getLogger(__name__)

    wmsg_id, wmsg_rule_id = set_welcome_message()
    logger.info("Mensaje de bienvenida establecido")

    def regfunc():
        sleep(10)
        id = register()
        logger.info(f"Aplicación registrada en Twitter con id: {id}")

    t = threading.Thread(target=regfunc)
    t.start()

    # Scheduler

    sched = BackgroundScheduler()

    PUT_INTERVAL = int(os.environ.get("PUT_INTERVAL", 10))

    @sched.scheduled_job('interval', minutes=PUT_INTERVAL)
    def timed_job():
        t = threading.Thread(target=put, kwargs={"print_log": False, "fail_register": True})
        t.run()
        print("Llamada a twitter para mantener el servidor activo")

    sched.start()

    # Clean-up code

    def exitfunc_unregister():
        unregister()
        logger.info("Aplicación desuscrita de la feed de Twitter")

    def exitfunc_remove_wmsg(wmsg_id, wmsg_rule_id):
        remove_welcome_message(wmsg_id, wmsg_rule_id)
        logger.info("Mensaje de bienvenida eliminado")

    atexit.register(exitfunc_remove_wmsg, wmsg_id, wmsg_rule_id)
    atexit.register(exitfunc_unregister)

application = get_wsgi_application()
