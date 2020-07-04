import requests
import requests_oauthlib
import sys
import chatbot.api_handler as api
from chatbot.config import APP_URL, TWITTER_ENV_NAME
from chatbot.welcomemsg import welcomemsgtext

def check(request):
    try:
        request.raise_for_status()
    except requests.HTTPError:
        code = request.json()["errors"][0]["code"]
        msg = request.json()["errors"][0]["message"]
        print(f"{code}: {msg}")

def register():
    r = requests.post(f"https://api.twitter.com/1.1/account_activity/all/{TWITTER_ENV_NAME}/webhooks.json", params={"url": APP_URL+"/webhook"}, auth=api.msgauth)
    check(r)
    id = r.json()["id"]
    r = requests.post(f"https://api.twitter.com/1.1/account_activity/all/{TWITTER_ENV_NAME}/subscriptions.json", auth=api.msgauth)
    check(r)
    return id

def unregister():
    r = requests.get(f"https://api.twitter.com/1.1/account_activity/all/webhooks.json", auth=api.msgauth)
    check(r)
    id = r.json()["environments"][0]["webhooks"][0]["id"]
    r = requests.delete(f"https://api.twitter.com/1.1/account_activity/all/{TWITTER_ENV_NAME}/webhooks/{id}.json", auth=api.msgauth)
    check(r)

def show():
    r = requests.get(f"https://api.twitter.com/1.1/account_activity/all/webhooks.json", auth=api.msgauth)
    check(r)
    try:
        id = r.json()["environments"][0]["webhooks"][0]["id"]
        env_name = r.json()["environments"][0]["environment_name"]
        print(f"env_name: ", env_name, ",\tid: ", id)
        return id
    except IndexError:
        print("No hay aplicaciones registradas")

def put(print=True):
    id = show()
    r = requests.put(f"https://api.twitter.com/1.1/account_activity/all/{TWITTER_ENV_NAME}/webhooks/{id}.json", auth=api.msgauth)
    check(r)
    if print:
        print("Done!")


def cleanwelcomemsg():
	#Messages
	r = requests.get("https://api.twitter.com/1.1/direct_messages/welcome_messages/list.json", auth=api.msgauth)
	r.raise_for_status()
	try:
		welcome_messages_ids = [welcome_message["id"] for welcome_message in r.json()["welcome_messages"]]
	except KeyError:
		welcome_messages_ids = []
	for wm_id in welcome_messages_ids:
		par = {
			"id": wm_id
		}
		r = requests.delete("https://api.twitter.com/1.1/direct_messages/welcome_messages/destroy.json", auth=api.msgauth, params=par)
		r.raise_for_status()
	#Rules
	r = requests.get("https://api.twitter.com/1.1/direct_messages/welcome_messages/rules/list.json", auth=api.msgauth)
	r.raise_for_status()
	try:
		welcome_rules_ids = [welcome_message_rule["id"] for welcome_message_rule in r.json()["welcome_message_rules"]]
	except KeyError:
		welcome_rules_ids = []
	for wr_id in welcome_rules_ids:
		par = {
			"id": wr_id
		}
		r = requests.delete("https://api.twitter.com/1.1/direct_messages/welcome_messages/rules/destroy.json", auth=api.msgauth, params=par)
		r.raise_for_status()

def set_welcome_message():
	welcomemsg = api.msg.create(None, welcomemsgtext)
	welcomemsg.setaswelcomemsg()
	return welcomemsg.welcomemessageid, welcomemsg.ruleid

def remove_welcome_message(wmsg_id, wmsg_rule_id):
	r = requests.delete("https://api.twitter.com/1.1/direct_messages/welcome_messages/destroy.json", auth=api.msgauth, params={"id": wmsg_id})
	r.raise_for_status()
	r = requests.delete("https://api.twitter.com/1.1/direct_messages/welcome_messages/rules/destroy.json", auth=api.msgauth, params={"id": wmsg_rule_id})
	r.raise_for_status()

if __name__ == "__main__":
    switch = {
        "register": register,
        "unregister": unregister,
        "list": show,
        "put": put,
        "cleanmsg": cleanwelcomemsg
    }
    try:
        option = sys.argv[1]
        switch[option]()
    except KeyError:
        print("Uso: webhook_tools [option]\n\t- register: Registra la app en Twitter\n\t- unregister: Borra la app del registro de twitter\n\t- list: Muestra las apps registradas en Twitter\n\t- put: Realiza una llamada a la app para comprobar que está activa")
    except IndexError:
        print("Uso: webhook_tools [option]\n\t- register: Registra la app en Twitter\n\t- unregister: Borra la app del registro de twitter\n\t- list: Muestra las apps registradas en Twitter\n\t- put: Realiza una llamada a la app para comprobar que está activa")
