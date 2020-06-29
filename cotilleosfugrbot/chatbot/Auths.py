import os

#Twitter api keys

keysinenviron = all([x in os.environ for x in ["CONSUMER_KEY", "CONSUMER_SECRET_KEY", "TOKEN_KEY", "TOKEN_SECRET_KEY"]])

if keysinenviron:
	consumer = os.environ.get("CONSUMER_KEY")
	consumer_secret = os.environ.get("CONSUMER_SECRET_KEY")
	token = os.environ.get("TOKEN_KEY")
	token_secret = os.environ.get("TOKEN_SECRET_KEY")
else:
	consumer = 'iFOzwbd9JaCF5hcQyiAuQiAKI'
	consumer_secret = 'B4WHCCOd8Z66AQcIGNZaAFWbhTu43ho8gXcQifrIfoi4WYrk0I'
	token = '1097946363512455175-cLpWgUVUmtTCuDy8xzi1TKl0jw7AH1'
	token_secret = 'DQrR73Nz5LHi34xkwhLznvvr7dZM8MldGIN0qtDjoWjRZ'


#IBM cloud key

keysinenviron = all([x in os.environ for x in ["IBM_CLOUD_KEY", "IBM_LANGUAGE_URL"]])

if keysinenviron:
	ibm_key = os.environ.get("IBM_CLOUD_KEY")
	ibm_language_url = os.environ.get("IBM_LANGUAGE_URL")
else:
	ibm_key = ""
	ibm_language_url = ""