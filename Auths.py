import os

keysinenviron = all([x in os.environ for x in ["CONSUMER_KEY", "CONSUMER_SECRET_KEY", "TOKEN_KEY", "TOKEN_SECRET_KEY"]])

if keysinenviron:
	consumer = os.environ.get("CONSUMER_KEY")
	consumer_secret = os.environ.get("CONSUMER_SECRET_KEY")
	token = os.environ.get("TOKEN_KEY")
	token_secret = os.environ.get("TOKEN_SECRET_KEY")
else:
	consumer = ''
	consumer_secret = ''
	token = ''
	token_secret = ''
