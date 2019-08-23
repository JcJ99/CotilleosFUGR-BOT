import cotilleosfugrbot
from cotilleosfugrbot import regthread, wakerthread, webhookunregister
from cotilleosfugrbot import app as application
from cleanwebhooks import cleanwelcomemsg
import logging
import signal

def signal_handler_wsgi(signum, frame):
	cleanwelcomemsg()
	webhookunregister(cotilleosfugrbot.appid)
	waker.event.set()

gunicorn_logger = logging.getLogger('gunicorn.error')
application.logger.handlers = gunicorn_logger.handlers
application.logger.setLevel(gunicorn_logger.level)
signal.signal(signal.SIGTERM, signal_handler_wsgi)
signal.signal(signal.SIGINT, signal_handler_wsgi)
reg = regthread()
waker = wakerthread()
waker.start()
reg.start()

if __name__ == "__main__":
	application.start()