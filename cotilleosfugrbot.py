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
from welcomemsg import welcomemsgtext
from cleanwebhooks import cleanwelcomemsg
#from pyngrok import ngrok

appid = ""

app = Flask(__name__)
conversations = []
welcomemsg = api.msg.create(None, welcomemsgtext)

class SIGTERM(BaseException):
	pass

def signal_handler_debug(signum, frame):
	raise SIGTERM()

def signal_handler_wsgi(signum, frame):
	cleanwelcomemsg()
	webhookunregister(appid)
	waker.event.set()
class regthread(threading.Thread):
	def __init__(self, time=3):
		threading.Thread.__init__(self)
		self.time = time
	def run(self):
		global appid
		sleep(self.time)
		try:
			r = requests.post("https://api.twitter.com/1.1/account_activity/all/" + TWITTER_ENV_NAME + "/webhooks.json", auth=msgauth, params={"url": APP_URL + "/webhook"})
			r.raise_for_status()
			appid = r.json()["id"]
			app.logger.critical("Aplicación registrada correctamente en Twitter con id: " + appid)
			subcribeforaccount()
			app.logger.critical("Recibiendo eventos del entorno: " + TWITTER_ENV_NAME)
			welcomemsg.setaswelcomemsg()
			app.logger.critical("Mensaje de bienvenida establecido")
			self.registered = True
		except requests.HTTPError:
			errormsg = r.json()["errors"][0]["message"]
			errorcode = r.json()["errors"][0]["code"]
			self.registered = False
			app.logger.error(f"TWITTER ERROR ({errorcode}): {errormsg}")
			if errorcode == 34:
				app.logger.error("No se ha podido conectar con Twitter. Revise que ha introucido el nombre del entorno de la aplicación de Twitter en el archivo config.py")
			elif errorcode == 215:
				app.logger.error("No se ha podido autenticar la cuenta de Twitter. Comprueba que el archivo Auths o las variables de entorno")
			elif errorcode == 214:
				app.logger.error("Ya hay demasiadas aplicaciones vinculadas a este entorno de Twitter, para eliminarlas todas ejecute python cleanwebhooks.py")

class wakerthread(threading.Thread):
	def __init__(self, timermin=20):
		threading.Thread.__init__(self)
		self.event = threading.Event()
		self.timermin = timermin
	def run(self):
		self.event.wait(60*self.timermin)
		while not self.event.is_set():
			r = requests.put("https://api.twitter.com/1.1/account_activity/all/" + TWITTER_ENV_NAME + "/webhooks/" + appid + ".json", auth=msgauth)
			self.event.wait(60*self.timermin)

def webhookunregister(appid):
	r = requests.delete("https://api.twitter.com/1.1/account_activity/all/" + TWITTER_ENV_NAME + "/webhooks/" + appid + ".json", auth=msgauth)
	r.raise_for_status()

def subcribeforaccount():
	r = requests.post("https://api.twitter.com/1.1/account_activity/all/" + TWITTER_ENV_NAME + "/subscriptions.json", auth=msgauth)
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
	for i,conversation in enumerate(conversations):
		try:
			delta = currtime - conversation.creationdate
			if delta > datetime.timedelta(days=2) and not conversation.punishment:
				del conversations[i]
		except AttributeError:
			del conversation

def convertojson(conver):
	conv_data = {
		"user_id": conver.user_id,
		"tweets": [tweet[0] for tweet in conver.tweets],
		"punishment_type": None,
		"punishment_end": None
	}
	if conver.punishment:
		conv_data["punishment_type"] = conver.punishment[0]
		if conver.punishment[0] == "timeout":
			conv_data["punishment_end"] = conver.punishment[1].strftime("%H:%M:%S %d/%m/%Y")
	return conv_data

def timeout(u_id, days):
	days = int(days)
	for conver in conversations:
		if u_id == conver.user_id:
			conver.timeout(days)
			return "OK"
	new_conv = conv.conversation(u_id)
	new_conv.timeout(days)
	conversations.append(new_conv)
	return "OK"

def ban(u_id):
	for conver in conversations:
		if u_id == conver.user_id:
			conver.ban()
			return "OK"
	new_conv = conv.conversation(u_id)
	new_conv.ban()
	conversations.append(new_conv)
	return "OK"

def forgive(u_id):
	for conver in conversations:
		if u_id == conver.user_id:
			conver.forgive()
			return "OK"
	return "El usuario introucido no tiene ningún castigo", 400

@app.route("/webhook", methods=["GET", "POST"])
def respond():
	if request.method == "GET":
		return challenge(request.args.get("crc_token"))
	elif request.method == "POST":
		data = request.get_json()
		associate(data)
		cleanconvers()
		return "OK"

@app.route("/admin", methods=["GET", "POST"])
def admin():
	if request.method == "GET":
		response = {
			"credentials": {
				"consumer": consumer,
				"consumer_secret": consumer_secret
			},
			"conversations": []
		}
		for conv in conversations:
			conv_data = convertojson(conv)
			response["conversations"].append(conv_data)
		return dumps(response)
	elif request.method == "POST":
		cleanconvers()
		command = request.headers.get("command")
		user_name = request.headers.get("user")
		try:
			user_id = api.getuserid(user_name)[0]
			if command == "timeout":
				days = request.args.get("days")
				return timeout(user_id, days)
			if command == "ban":
				return ban(user_id)
			if command == "forgive":
				return forgive(user_id)
		except requests.HTTPError:
			return "No existe el usuario @" + user_name, 400



"""if __name__ != "__main__":
	gunicorn_logger = logging.getLogger('gunicorn.error')
	app.logger.handlers = gunicorn_logger.handlers
	app.logger.setLevel(gunicorn_logger.level)
	signal.signal(signal.SIGTERM, signal_handler_wsgi)
	signal.signal(signal.SIGINT, signal_handler_wsgi)
	reg = regthread(10)
	waker = wakerthread()
	waker.start()
	if APP_URL[len(APP_URL)-1] == "/":
		url = url[:len(url)-1]
	app.logger.info("Servidor abierto con url: " +  APP_URL)
	reg.start()"""

if __name__ == "__main__":
	signal.signal(signal.SIGTERM, signal_handler_debug)
	port = int(os.environ.get('PORT', 5000))
	APP_URL = ngrok.connect(port=port)
	APP_URL = "https://" + APP_URL.split("//")[1]
	print("Registro de eventos: http://localhost:4040")
	reg = regthread(5)
	if APP_URL[len(APP_URL)-1] == "/":
		url = url[:len(url)-1]
	print("Servidor abierto con url: " +  APP_URL)
	try:
		reg.start()
		app.run(host="0.0.0.0",port=port)
	except KeyboardInterrupt:
		cleanwelcomemsg()
		pass
	except SIGTERM:
		cleanwelcomemsg()
		pass
	finally:
		app.logger.warning("Saliendo...")
		cleanwelcomemsg()
		webhookunregister(appid)
		ngrok.disconnect(APP_URL)