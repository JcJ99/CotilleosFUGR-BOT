from . import api_handler as api
from . import conver_handler as conv
from .models import User, Tweet
import logging

logger = logging.getLogger(__name__)

conversations = []

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
	elif "tweet_delete_events" in jsondata.keys():
		return "del"
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
		user = User.objects.filter(id=int(uid))
		if not user:
			return None
		else:
			conversations.append(conv.conversation.from_model(user[0]))
			return len(conversations) - 1
	if typ == "fav":
		tid = jsondata["favorite_events"][0]["favorited_status"]["id"]
		twt = Tweet.objects.filter(id=int(tid))[0]
		if not twt:
			return None
		else:
			uid = twt.user.id
			for c in conversations:
				if int(c.user_id) == uid:
					return index
				index += 1
			conversations.append(conv.conversation.from_model(twt.user))
			return len(conversations) - 1
	if typ in ["rt", "quote", "reply"]:
		if typ == "quote":
			tid = jsondata["tweet_create_events"][0]["quoted_status_id"]
			twt = Tweet.objects.filter(id=int(tid))[0]
			if not twt:
				return None
			else:
				uid = twt.user.id
				for c in conversations:
					if int(c.user_id) == uid:
						return index
					index += 1
				conversations.append(conv.conversation.from_model(twt.user))
				return len(conversations) - 1
		else:
			uid = jsondata["tweet_create_events"][0]["user"]["id"]
			if (str(uid) == api.selfid):
				return -1
			for c in conversations:
				if c.user_id == str(uid):
					return index
				index += 1
			user = User.objects.filter(id=int(uid))
			if not user:
				return None
			else:
				conversations.append(conv.conversation.from_model(user[0]))
				return len(conversations) - 1
	if typ == "del":
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
				"""if msg.rawtext()[0] == "/":
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
				else:"""
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
		elif typ == "del":
			tid = jsondata["tweet_delete_events"][0]["status"]["id"]
			t_db = Tweet.objects.filter(id=int(tid))
			t_db.delete()


def cleanconvers():
	for i,c in enumerate(conversations):
		if not c.editingtweets():
			conversations.pop(i)