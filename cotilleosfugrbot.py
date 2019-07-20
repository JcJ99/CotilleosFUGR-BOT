import conver_handler as conv
import api_handler as api
from flask import Flask, request
import requests
from api_handler import msgauth
import sys
import threading
from time import sleep
import datetime
from Auths import *
import base64
import hashlib
import hmac
from json import dumps
import logging
import signal
from config import *

#Remove flask output
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

appid = ""

app = Flask(__name__)
conversations = []

class SIGTERM(BaseException):
	pass

def signal_handler(signum, frame):
	raise SIGTERM()

class regthread(threading.Thread):
	def __init__(self, time=3):
		threading.Thread.__init__(self)
		self.time = time
	def run(self):
		global appid
		sleep(self.time)
		try:
			r = requests.post("https://api.twitter.com/1.1/account_activity/all/" + twitterenvname + "/webhooks.json", auth=msgauth, params={"url": appurl + "/webhook"})
			r.raise_for_status()
			appid = r.json()["id"]
			print("Aplicación registrada correctamente en Twitter con id: " + appid, file=sys.stderr)
			subcribeforaccount()
			print("Recibiendo eventos del entorno: " + twitterenvname)
			print("Ctrl+C Para salir")
			self.registered = True
		except requests.HTTPError:
			errormsg = r.json()["errors"][0]["message"]
			errorcode = r.json()["errors"][0]["code"]
			self.registered = False
			print(f"TWITTER ERROR ({errorcode}): {errormsg}")
			if errorcode == 34:
				print("No se ha podido conectar con Twitter. Revise que ha introucido el nombre del entorno de la aplicación de Twitter en el archivo config.py")
			elif errorcode == 215:
				print("No se ha podido autenticar la cuenta de Twitter. Comprueba que el archivo Auths o las variables de entorno")
			elif errorcode == 214:
				print("Ya hay demasiadas aplicaciones vinculadas a este entorno de Twitter, para eliminarlas todas ejecute python cleanwebhooks.py")
			print("Ctrl+C Para salir")

def webhookunregister(appid):
	r = requests.delete("https://api.twitter.com/1.1/account_activity/all/" + twitterenvname + "/webhooks/" + appid + ".json", auth=msgauth)
	r.raise_for_status()

def subcribeforaccount():
	r = requests.post("https://api.twitter.com/1.1/account_activity/all/" + twitterenvname + "/subscriptions.json", auth=msgauth)
	r.raise_for_status()

def challenge(crc_token):
	b = bytearray()
	b.extend(map(ord, crc_token))
	b2 = bytearray()
	b2.extend(map(ord, consumer_secret))
	sha256_hash_digest = hmac.new(b2, msg=b, digestmod=hashlib.sha256).digest()
	response = {
		'response_token': 'sha256=' + "".join(map(chr, base64.b64encode(sha256_hash_digest)))
	}
	return dumps(response)

def identify(jsondata):
	if "direct_message_events" in jsondata.keys():
		return "dm"
	elif "favorite_events" in jsondata.keys():
		return "fav"
	elif "tweet_create_events" in jsondata.keys():
		if "retweeted_status" in jsondata["tweet_create_events"][0]:
			return "rt"
		elif "quoted_status" in jsondata["tweet_create_events"][0]:
			return "quote"
		elif "in_reply_to_status_id" != None:
			return "reply"
	else:
		return None


def knownuser(jsondata):
	typ = identify(jsondata)
	index = 0
	if typ == "dm":
		uid = jsondata["direct_message_events"][0]["message_create"]["sender_id"]
		if uid == str(api.selfid):
			return -1
		for c in conversations:
			if c.user_id == uid:
				return index
			index += 1
		return None
	if typ == "fav":
		tid = jsondata["favorite_events"][0]["favorited_status"]["id"]
		for c in conversations:
			for tweet in c.tweets:
				if tid == tweet[0]:
					return index
			index += 1
		return None
	if typ in ["rt", "quote", "reply"]:
		if typ == "quote":
			tid = jsondata["tweet_create_events"][0]["quoted_status_id"]
			for c in conversations:
				for tweet in c.tweets:
					if tid == tweet[0]:
						return index
				index += 1
			return None
		else:
			uid = jsondata["tweet_create_events"][0]["user"]["id"]
			if (str(uid) == api.selfid):
				return -1
			for c in conversations:
				if c.user_id == str(uid):
					return index
				index += 1
			return None

def associate(jsondata):
	typ = identify(jsondata)
	index = knownuser(jsondata)
	if index == -1:
		pass
	else:
		if typ == "dm":
			msg = api.msg(jsondata["direct_message_events"][0])
			if index == None:
				conversations.append(conv.conversation(msg.sid()))
				conversations[len(conversations) - 1].read(msg)
			else:
				conversations[index].read(msg)
		elif typ == "fav":
			if index == None:
				pass
			else:
				fav = jsondata["favorite_events"][0]
				user = fav["user"]["screen_name"]
				link = "https://twitter.com/" + api.selfscreenname + "/status/" + fav["favorited_status"]["id_str"]
				text = "A @" + user + " le ha gustado tu tweet"
				conversations[index].notify(text, link)
		elif typ == "rt":
			if index == None:
				pass
			else:
				rt = jsondata["tweet_create_events"][0]
				user = rt["user"]["screen_name"]
				link = "https://twitter.com/" + api.selfscreenname + "/status/" + rt["retweeted_status"]["id_str"]
				text = "@" + user + " ha retwiteado tu tweet"
				conversations[index].notify(text, link)
		elif typ == "quote":
			if index == None:
				pass
			else:
				quote = jsondata["tweet_create_events"][0]
				user = quote["user"]["screen_name"]
				link = "https://twitter.com/" + api.selfscreenname + "/status/" + quote["id_str"]
				text = "@" + user + " ha citado tu tweet"
				conversations[index].notify(text, link)
		elif typ == "reply":
			if index == None:
				pass
			else:
				reply = jsondata["tweet_create_events"][0]
				user = reply["user"]["screen_name"]
				link = "https://twitter.com/" + api.selfscreenname + "/status/" + reply["id_str"]
				text = "@" + user + " ha respondido a tu tweet"
				conversations[index].notify(text, link)

def cleanconvers():
	currtime = datetime.datetime.now()
	for conversation in conversations:
		try:
			delta = currtime - conversation.creationdate
			if delta > datetime.timedelta(days=2):
				del conversation
		except AttributeError:
			del conversation

@app.route("/webhook", methods=["GET", "POST"])
def respond():
	if request.method == "GET":
		return challenge(request.args.get("crc_token"))
	elif request.method == "POST":
		data = request.get_json()
		associate(data)
		cleanconvers()
		return "OK"

if __name__ == "__main__":
	signal.signal(signal.SIGTERM, signal_handler)
	onheroku = os.environ.get("ONHEROKU", 0)
	if onheroku:
		port = int(os.environ.get('PORT', 33507))
		reg = regthread(8)
	else:
		from pyngrok import ngrok
		port = int(os.environ.get('PORT', 5000))
		appurl = ngrok.connect(port=port)
		appurl = "https://" + appurl.split("//")[1]
		print("Registro de eventos: http://localhost:4040")
		reg = regthread(1)
	print("Servidor abierto con url: " +  appurl)
	try:
		reg.start()
		app.run(host="0.0.0.0",port=port)
	except KeyboardInterrupt:
		pass
	except SIGTERM:
		pass
	finally:
		print("\nSaliendo...")
		if reg.registered:
			webhookunregister(appid)
		if not onheroku:
			ngrok.disconnect(appurl)