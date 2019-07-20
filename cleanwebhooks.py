import requests
from api_handler import msgauth

#Get all webhooks
r = requests.get("https://api.twitter.com/1.1/account_activity/all/webhooks.json", auth=msgauth)
r.raise_for_status()
for env in r.json()["environments"]:
	envname = env["environment_name"]
	for wh in env["webhooks"]:
		r2 = requests.delete("https://api.twitter.com/1.1/account_activity/all/"+envname+"/webhooks/"+wh["id"]+".json", auth=msgauth)
		r.raise_for_status()