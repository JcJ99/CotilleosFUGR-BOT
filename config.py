import os

APP_URL = "" #No usar / al final de la url
TWITTER_ENV_NAME = ""
MAX_TWEETS_PER_HOUR = 5

if "APP_URL" in os.environ:
	APP_URL = os.environ.get("APP_URL")
if "TWITTER_ENV_NAME" in os.environ:
	TWITTER_ENV_NAME = os.environ.get("APP_URL")
if "MAX_TWEETS_PER_HOUR" in os.environ:
	MAX_TWEETS_PER_HOUR = os.environ.get("MAX_TWEETS_PER_HOUR")