import os

APP_URL = "https://62d6cff0a234.ngrok.io" #HTTPS URL
DATABASE_URL = "postgres://gbzirvnrqtykdz:4a44c3903c9637f20647b0b25bc1959a6e6238d6d69d305ea9500546bbd7f56b@ec2-54-75-249-16.eu-west-1.compute.amazonaws.com:5432/d85ah1um8lrfjn"
TWITTER_ENV_NAME = "dev"
MAX_TWEETS_PER_HOUR = 5
ADMIN_PASS = ""
SPAM_NEGATIVE_LIMIT = -1
SCORE_ZERO_ERROR = 0

if "APP_URL" in os.environ:
	APP_URL = os.environ.get("APP_URL")
if "TWITTER_ENV_NAME" in os.environ:
	TWITTER_ENV_NAME = os.environ.get("TWITTER_ENV_NAME")
if "MAX_TWEETS_PER_HOUR" in os.environ:
	MAX_TWEETS_PER_HOUR = os.environ.get("MAX_TWEETS_PER_HOUR")
if "DATABASE_URL" in os.environ:
	DATABASE_URL = os.environ.get("DATABASE_URL")
if "ADMIN_PASS" in os.environ:
	ADMIN_PASS = os.environ.get("ADMIN_PASS")
if "SPAM_NEGATIVE_LIMIT" in os.environ:
	SPAM_NEGATIVE_LIMIT = os.environ.get("SPAM_NEGATIVE_LIMIT")
if "SCORE_ZERO_ERROR" in os.environ:
	SCORE_ZERO_ERROR = os.environ.get("SCORE_ZERO_ERROR")