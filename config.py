import os

APP_URL = "" #HTTPS URL
TWITTER_ENV_NAME = "chatbot"
MAX_TWEETS_PER_HOUR = 5

if "APP_URL" in os.environ:
	APP_URL = os.environ.get("APP_URL")
if "TWITTER_ENV_NAME" in os.environ:
	TWITTER_ENV_NAME = os.environ.get("TWITTER_ENV_NAME")
if "MAX_TWEETS_PER_HOUR" in os.environ:
	MAX_TWEETS_PER_HOUR = os.environ.get("MAX_TWEETS_PER_HOUR")