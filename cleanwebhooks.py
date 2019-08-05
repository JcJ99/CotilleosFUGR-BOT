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

def cleanwelcomemsg():
	#Messages
	r = requests.get("https://api.twitter.com/1.1/direct_messages/welcome_messages/list.json", auth=msgauth)
	r.raise_for_status()
	try:
		welcome_messages_ids = [welcome_message["id"] for welcome_message in r.json()["welcome_messages"]]
	except KeyError:
		welcome_messages_ids = []
	for wm_id in welcome_messages_ids:
		par = {
			"id": wm_id
		}
		r = requests.delete("https://api.twitter.com/1.1/direct_messages/welcome_messages/destroy.json", auth=msgauth, params=par)
		r.raise_for_status()
	#Rules
	r = requests.get("https://api.twitter.com/1.1/direct_messages/welcome_messages/rules/list.json", auth=msgauth)
	r.raise_for_status()
	try:
		welcome_rules_ids = [welcome_message_rule["id"] for welcome_message_rule in r.json()["welcome_message_rules"]]
	except KeyError:
		welcome_rules_ids = []
	for wr_id in welcome_rules_ids:
		par = {
			"id": wr_id
		}
		r = requests.delete("https://api.twitter.com/1.1/direct_messages/welcome_messages/rules/destroy.json", auth=msgauth, params=par)
		r.raise_for_status()