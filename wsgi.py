import cotilleosfugrbot
from cotilleosfugrbot import regthread, wakerthread, webhookunregister
from cotilleosfugrbot import app as application
from cleanwebhooks import cleanwelcomemsg
import logging
import signal
from requests.exceptions import HTTPError

def signal_handler_wsgi(signum, frame):
	cleanwelcomemsg()
	try:
		webhookunregister(cotilleosfugrbot.appid)
	except HTTPError as e:
		if e.response.status_code == 404:
			pass
		else:
			raise
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