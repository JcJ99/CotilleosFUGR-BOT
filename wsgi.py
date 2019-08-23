from cotilleosfugrbot import app
import logging

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)
signal.signal(signal.SIGTERM, signal_handler_wsgi)
signal.signal(signal.SIGINT, signal_handler_wsgi)
reg = regthread(10)
waker = wakerthread()
waker.start()
if APP_URL[len(APP_URL)-1] == "/":
	url = url[:len(url)-1]
#app.logger.info("Servidor abierto con url: " +  APP_URL)
reg.start()

if __name__ == "__main__":
	app.start()