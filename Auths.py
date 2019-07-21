import os

keysinenviron = all([x in os.environ for x in ["CONSUMER_KEY", "CONSUMER_SECRET_KEY", "TOKEN_KEY", "TOKEN_SECRET_KEY"]])

if keysinenviron:
	consumer = os.environ.get("CONSUMER_KEY")
	consumer_secret = os.environ.get("CONSUMER_SECRET_KEY")
	token = os.environ.get("TOKEN_KEY")
	token_secret = os.environ.get("TOKEN_SECRET_KEY")
else:
	consumer = 'N6PMDWH1Tf8qIyN3qelmOviKU'
	consumer_secret = '5NymuUT1o4NtDcsPngeXd1bfNYqoBlsZuP5tSrnXZRQWIXdEw3'
	token = '289500652-4znRPvzQ5wcpYXZyPpDmJ3tN7UHUFHb4BjakLWwh'
	token_secret = 'o7PMtua6AoAR7v2pROaLLevaax8RZx5HFJnqsk8jrfDxY'
