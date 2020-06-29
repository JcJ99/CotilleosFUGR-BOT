import requests
import requests_oauthlib
import sys
from chatbot.api_handler import msgauth
from chatbot.config import APP_URL, TWITTER_ENV_NAME


def register():
    r = requests.post(f"https://api.twitter.com/1.1/account_activity/all/{TWITTER_ENV_NAME}/webhooks.json", params={"url": APP_URL+"/webhook"}, auth=msgauth)
    r.raise_for_status()
    r = requests.post(f"https://api.twitter.com/1.1/account_activity/all/{TWITTER_ENV_NAME}/subscriptions.json", auth=msgauth)
    r.raise_for_status()

def unregister():
    r = requests.get(f"https://api.twitter.com/1.1/account_activity/all/webhooks.json", auth=msgauth)
    r.raise_for_status()
    id = r.json()["environments"][0]["webhooks"][0]["id"]
    r = requests.delete(f"https://api.twitter.com/1.1/account_activity/all/{TWITTER_ENV_NAME}/webhooks/{id}.json", auth=msgauth)
    r.raise_for_status()

def show():
    r = requests.get(f"https://api.twitter.com/1.1/account_activity/all/webhooks.json", auth=msgauth)
    r.raise_for_status()
    id = r.json()["environments"][0]["webhooks"][0]["id"]
    env_name = r.json()["environments"][0]["environment_name"]
    print(f"env_name: ", env_name, "\tid: ", id)
    return id

def put():
    id = show()
    r = requests.put(f"https://api.twitter.com/1.1/account_activity/all/{TWITTER_ENV_NAME}/webhooks/{id}.json", auth=msgauth)
    r.raise_for_status()
    print("Done!")

if __name__ == "__main__":
    switch = {
        "register": register,
        "unregister": unregister,
        "list": show,
        "put": put
    }
    try:
        option = sys.argv[1]
        switch[option]()
    except KeyError:
        print("Uso: webhook_tools [option]\n\t- register: Registra la app en Twitter\n\t- unregister: Borra la app del registro de twitter\n\t- list: Muestra las apps registradas en Twitter\n\t- put: Realiza una llamada a la app para comprobar que está activa")
    except IndexError:
        print("Uso: webhook_tools [option]\n\t- register: Registra la app en Twitter\n\t- unregister: Borra la app del registro de twitter\n\t- list: Muestra las apps registradas en Twitter\n\t- put: Realiza una llamada a la app para comprobar que está activa")
