import os

APP_URL = "" #HTTPS URL
DATABASE_URL = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % {
	"user": "",
	"pw": "",
	"db": "",
	"host": "",
	"port": "5432" #Usual port
} #Prepared for PostgrelSQL
TWITTER_ENV_NAME = ""
MAX_TWEETS_PER_HOUR = 5
ADMIN_PASS = ""

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