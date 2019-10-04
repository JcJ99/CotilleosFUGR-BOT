import conver_handler as conv
import api_handler as api
from flask import Flask, request
import requests
from api_handler import msgauth
import sys
import threading
from time import sleep, tzset
import datetime
from Auths import *
import base64
import hashlib
from urllib.parse import quote_plus
import hmac
import json
import logging
import signal
from config import *
from welcomemsg import welcomemsgtext
from cleanwebhooks import cleanwelcomemsg
from flask_sqlalchemy import SQLAlchemy

appid = ""

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
db = SQLAlchemy(app)
conversations = []
welcomemsg = api.msg.create(None, welcomemsgtext)
if APP_URL != "" and APP_URL[len(APP_URL)-1] == "/":
	APP_URL = APP_URL[:len(url)-1]
tzset()

class Conversation_model(db.Model):
	__tablename__ = "conversations"
	id = db.Column(db.BigInteger, primary_key=True)
	tweets = db.relationship("Tweet_model", backref="conversation", lazy=True)
	creation_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
	punishment_type = db.Column(db.String(7), default=None)
	punishment_end = db.Column(db.DateTime, default=None)
	admin = db.Column(db.Boolean, default=False)

	def __repr__(self):
		return "<Conversation: %r>" % self.id

class Tweet_model(db.Model):
	__tablename__ = "tweets"
	id = db.Column(db.BigInteger, primary_key=True)
	creation_date = db.Column(db.DateTime, nullable=False)
	conversation_id = db.Column(db.BigInteger, db.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)

	def __repr__(self):
		return "<Tweet: %r>" % self.id

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
			app.logger.critical("Servidor abierto con url: " +  APP_URL)
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
		first_try = True
		while not self.event.is_set():
			if not first_try:
				r = requests.put("https://api.twitter.com/1.1/account_activity/all/" + TWITTER_ENV_NAME + "/webhooks/" + appid + ".json", auth=msgauth)
			first_try = False
			self.event.wait(60*self.timermin)

class databaseupdaterthread(threading.Thread):
	def __init__(self, conver, wait=20):
		threading.Thread.__init__(self)
		self.conver = conver
		self.wait = wait
	def run(self):
		sleep(self.wait)
		update_database(self.conver)

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
	return json.dumps(response)

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
		conver = Conversation_model.query.get(int(uid))
		if conver is None:
			return None
		else:
			conversations.append(conv.conversation.from_model(conver))
			return len(conversations) - 1
	if typ == "fav":
		tid = jsondata["favorite_events"][0]["favorited_status"]["id"]
		for c in conversations:
			for tweet in c.tweets:
				if tid == tweet[0]:
					return index
			index += 1
		twt = Tweet_model.query.get(tid)
		if twt is None:
			return None
		else:
			conversations.append(conv.conversation.from_model(twt.conversation))
			return len(conversations) - 1
	if typ in ["rt", "quote", "reply"]:
		if typ == "quote":
			tid = jsondata["tweet_create_events"][0]["quoted_status_id"]
			for c in conversations:
				for tweet in c.tweets:
					if tid == tweet[0]:
						return index
				index += 1
			twt = Tweet_model.query.get(tid)
			if twt == None:
				return None
			else:
				conversations.append(conv.conversation.from_model(twt.conversation))
				return len(conversations) - 1
		else:
			uid = jsondata["tweet_create_events"][0]["user"]["id"]
			if (str(uid) == api.selfid):
				return -1
			for c in conversations:
				if c.user_id == str(uid):
					return index
				index += 1
			conver = Conversation_model.query.get(int(uid))
			if conver is None:
				return None
			else:
				conversations.append(conv.conversation.from_model(conver))
				return len(conversations) - 1

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
				if msg.rawtext()[0] == "/":
					if conversations[index].isadmin:
						switcher = {
							"ban": admin_ban,
							"timeout": admin_timeout
						}
						command = msg.rawtext()[1::].split()
						if len(command) < 2:
							command.append(None)
						try:
							if "t.co" in command[1].split("/"):
								command[1] = msg.url()
						except AttributeError:
							pass
						user = admin_identify(index, *tuple(command[1::]))
						if user:
							if user != -1:
								command[1] = user
								switcher[command[0]](index, *tuple(command[1::]))
							else:
								if command[0] in switcher.keys():
									conversations[index].notify("Introduce el link de un tweet para aplicar el comando", critical=True)
								else:
									conversations[index].notify("Comandos disponibles:\n	\u2022	ban <Link/Id del tweet>\n	\u2022	timeout <Link/Id del tweet> <Días>")
					else:
						conversations[index].notify("No tienes permisos de administrador para ejecutar comandos", critical=True)
				else:
					if conversations[index].read(msg):
						#If send command received
						t = databaseupdaterthread(conversations[index])
						t.start()

		elif typ == "fav":
			if index == None:
				pass
			else:
				fav = jsondata["favorite_events"][0]
				user = fav["user"]["screen_name"]
				link = "https://twitter.com/" + api.selfscreenname + "/status/" + fav["favorited_status"]["id_str"]
				text = "A @" + user + " le ha gustado tu tweet"
				conversations[index].notify(text, link)
				if not conversations[index].editingtweets:
					del conversations[index]
		elif typ == "rt":
			if index == None:
				pass
			else:
				rt = jsondata["tweet_create_events"][0]
				user = rt["user"]["screen_name"]
				link = "https://twitter.com/" + api.selfscreenname + "/status/" + rt["retweeted_status"]["id_str"]
				text = "@" + user + " ha retwiteado tu tweet"
				conversations[index].notify(text, link)
				if not conversations[index].editingtweets:
					del conversations[index]
		elif typ == "quote":
			if index == None:
				pass
			else:
				quote = jsondata["tweet_create_events"][0]
				user = quote["user"]["screen_name"]
				link = "https://twitter.com/" + api.selfscreenname + "/status/" + quote["id_str"]
				text = "@" + user + " ha citado tu tweet"
				conversations[index].notify(text, link)
				if not conversations[index].editingtweets:
					del conversations[index]
		elif typ == "reply":
			if index == None:
				pass
			else:
				reply = jsondata["tweet_create_events"][0]
				user = reply["user"]["screen_name"]
				link = "https://twitter.com/" + api.selfscreenname + "/status/" + reply["id_str"]
				text = "@" + user + " ha respondido a tu tweet"
				conversations[index].notify(text, link)
				if not conversations[index].editingtweets:
					del conversations[index]

def admin_ban(index, *args):
	try:
		user_id = args[0]
	except IndexError:
		conversations[index].notify("Uso: ban <Link/Id del tweet>", critical=True)
		return
	except ValueError:
		conversations[index].notify("Uso: ban <Link/Id del tweet>", critical=True)
		return
	except requests.exceptions.HTTPError as e:
		if e.response.status_code == 404:
			conversations[index].notify("El usuario no existe", critical=True)
			return

	user = Conversation_model.query.get(user_id)
	if user:
		user.punishment_type = "ban"
		db.session.commit()
	else:
		user = Conversation_model(id=user_id, punishment_type="ban")
		db.session.add(user)
		db.session.commit()
	
	conversations[index].notify("Usuario castigado correctamente", critical=True)

def admin_timeout(index, *args):
	try:
		user_id = args[0]
		days = args[1]
		days = int(days)
	except IndexError:
		conversations[index].notify("Uso: timeout <Link/Id del tweet> <dias (Nº Entero)>", critical=True)
		return
	except ValueError:
		conversations[index].notify("Uso: timeout <Link/Id del tweet> <dias (Nº Entero)>", critical=True)
		return
	except requests.exceptions.HTTPError as e:
		if e.response.status_code == 404:
			conversations[index].notify("El usuario no existe", critical=True)
			return

	user = Conversation_model.query.get(user_id)
	if user:
		user.punishment_type = "timeout"
		user.punishment_end = datetime.datetime.utcnow() + datetime.timedelta(days=days)
		db.session.commit()
	else:
		user = Conversation_model(id=user_id, punishment_type="timeout", punishment_end=datetime.datetime.utcnow() + datetime.timedelta(days=days))
		db.session.add(user)
		db.session.commit()
	
	conversations[index].notify("Usuario castigado correctamente", critical=True)

def admin_identify(index, *args):
	command_input = args[0]
	try:
		tweet_id = int(command_input)
	except ValueError:
		splitted = command_input.split("/")
		if "twitter.com" in splitted:
			if "https:" in splitted:
				tweet_id = int(splitted[5])
			else:
				tweet_id = int(splitted[3])
		else:
			conversations[index].notify("Link no válido", critical=True)
			return
	except TypeError:
		raise
	
	tweet = Tweet_model.query.get(tweet_id)
	if tweet:
		user_id = tweet.conversation.id
		return user_id
	else:
		return

def update_database(conver):
	global conversations
	c = Conversation_model.query.get(int(conver.user_id))
	if c is None:
		if conver.punishment:
			if conver.punishment[0] == "timeout":
				c = Conversation_model(id=int(conver.user_id), punishment_type="timeout", punishment_end=conver.punishment[1])
			elif conver.punishment[0] == "ban":
				c = Conversation_model(id=int(conver.user_id), punishment_type="ban")
		else:
			c = Conversation_model(id=int(conver.user_id))
		db.session.add(c)
		tweets_to_add = [Tweet_model(id=tweet[0], creation_date=tweet[1], conversation_id=int(conver.user_id)) for tweet in conver.tweets]
		db.session.add_all(tweets_to_add)
		db.session.commit()
	else:
		known_tweets_id = [tweet.id for tweet in c.tweets]
		tweets_to_add = [Tweet_model(id=tweet[0], creation_date=tweet[1], conversation_id=int(conver.user_id)) for tweet in conver.tweets if tweet[0] not in known_tweets_id]
		db.session.add_all(tweets_to_add)
		db.session.commit()

def cleanconvers():
	minimum_date = datetime.datetime.now() - datetime.timedelta(days=14)
	con = Conversation_model.query.filter(Conversation_model.creation_date < minimum_date, Conversation_model.punishment_type not in ["ban"]).all()
	for c in con:
		if not c.punishment_type and c.punishment_end < datetime.datetime.now():
			db.session.delete(c)
		db.session.commit()
	for i,conversation in enumerate(conversations):
		try:
			if not conversation.editingtweets():
				del conversations[i]
		except AttributeError:
			del conversation

def getbearertoken(consumer, consumer_secret):
	encoded_consumer = quote_plus(consumer)
	encoded_consumer_secret = quote_plus(consumer_secret)
	key_to_send = encoded_consumer + ":" + encoded_consumer_secret
	key_to_send = base64.b64encode(key_to_send.encode())
	headers = {
		"Authorization": "Basic " + key_to_send.decode(),
		"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
	}
	params = {"grant_type": "client_credentials"}
	r = requests.post("https://api.twitter.com/oauth2/token", headers=headers, params=params)
	return r.json()["access_token"]

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
		psw = request.headers.get("password")
		if psw == ADMIN_PASS:
			return {
				"database_url": DATABASE_URL,
				"bearer_token": getbearertoken(consumer, consumer_secret)
			}
		else:
			return "Contraseña no válida", 400

if __name__ == "__main__":
	signal.signal(signal.SIGTERM, signal_handler_debug)
	port = int(os.environ.get('PORT', 8000))
	print("Registro de eventos: http://localhost:4040")
	reg = regthread()
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