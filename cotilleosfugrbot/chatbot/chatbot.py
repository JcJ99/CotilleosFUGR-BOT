from . import api_handler as api
from . import conver_handler as conv
from .models import User, Tweet
import logging
import datetime

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
				if msg.rawtext()[0] == "/":
					conversations[len(conversations) - 1].notify("Debes publicar al menos un Tweet para acceder a los comandos", critical=True)
				conversations[len(conversations) - 1].read(msg)
			else:
				if msg.rawtext()[0] == "/":
					command = msg.rawtext()[1::].split()
					try:
						if command[0] == "noti":
							conversations[index].changenoti()
							if conversations[index].noti:
								word = "ACTIVADAS"
							else:
								word = "DESACTIVADAS"
							conversations[index].notify(f"Las notificaciones de la actividad de tus tweets están ahora {word}", critical=True)
							return
						elif (command[0] in ["ban", "timeout"]):
							if conversations[index].isadmin:
								if command[0] == "ban":
									try:
										if command[1] == "link":
											try:
												turl = msg.url()
												tid = int(turl.split("/")[5])
												try:
													t_db = Tweet.objects.get(id=tid)
													u_db = t_db.user
													u_db.punishment_type = "BAN"
													u_db.save()
													uname = api.getusername(u_db.id)[0]
													conversations[index].notify(f"El usuario @{uname} ha sido baneado correctamente", critical=True)
												except Tweet.DoesNotExist:
													conversations[index].notify("Este tweet no está registrado en la base de datos", critical=True)
												return
											except api.NoUrlException:
												raise IndexError
										elif command[1] == "user":
											u = command[2]
											try:
												uid = api.getuserid(u)[0]
												u_db = User.objects.get(id=int(uid))
												u_db.punishment_type = "BAN"
												u_db.save()
												conversations[index].notify(f"El usuario @{u} ha sido baneado correctamente", critical=True)
											except api.NoidException:
												conversations[index].notify(f"El usuario @{u} no existe")
											except User.DoesNotExist:
												u_db = User(id=int(uid), punishment_type="BAN")
												u_db.save()
												conversations[index].notify(f"El usuario @{u} ha sido baneado correctamente", critical=True)
											return
										else:
											raise IndexError
									except IndexError:
										conversations[index].notify("Uso: /ban [link/user] [tweet_link/username]", critical=True)
										return
								if command[0] == "timeout":
									try:
										if command[1] == "link":
											try:
												turl = msg.url()
												tid = int(turl.split("/")[5])
												try:
													days = int(command[3])
												except ValueError:
													raise IndexError
												try:
													t_db = Tweet.objects.get(id=int(tid))
													u_db = t_db.user
													u_db.punishment_type = "TMO"
													u_db.punishment_end = datetime.datetime.utcnow() + datetime.timedelta(days=days)
													u_db.save()
													uname = api.getusername(u_db.id)[0]
													date_string = u_db.punishment_end.strftime("%d/%m/%Y, %H:%M:%S UTC")
													conversations[index].notify(f"El usuario @{uname} no podrá twittear hasta: {date_string}")
												except Tweet.DoesNotExist:
													conversations[index].notify("El tweet no está registrado en la base de datos")
												return
											except api.NoUrlException:
												raise IndexError
										elif command[1] == "user":
											u = command[2]
											try:
												days = int(command[3])
											except ValueError:
												raise IndexError
											try:
												uid = api.getuserid(u)[0]
												u_db = User.objects.get(id=int(uid))
												u_db.punishment_type = "TMO"
												u_db.punishment_end = datetime.datetime.utcnow() + datetime.timedelta(days=days)
												u_db.save()
												date_string = u_db.punishment_end.strftime("%d/%m/%Y, %H:%M:%S UTC")
												conversations[index].notify(f"El usuario @{u} no podrá twittear hasta: {date_string}")
											except api.NoidException:
												conversations[index].notify(f"El usuario @{u} no existe")
											except User.DoesNotExist:
												p_end = datetime.datetime.utcnow() + datetime.timedelta(days=days)
												u_db = User(id=int(uid), punishment_type="TMO", punishment_end=p_end)
												u_db.save()
												conversations[index].notify(f"El usuario @{u} no podrá twittear hasta: {date_string}")
											return
										else:
											raise IndexError
									except IndexError:
										conversations[index].notify("Uso: /timeout [link/user] [tweet_link/username] [días]", critical=True)
							else:
								conversations[index].notify("No tienes permisos para hacer uso de este comando", critical=True)
								return
						else:
							conversations[index].notify("""Comandos disponibles:
													   \t\u2022 /noti: Activa o desactiva las notificaciones de tus tweets
													   \t\u2022 /ban: Evita que un usuario pueda twittear [ADMIN]
													   \t\u2022 /timeout: Evita que un usuario pueda twittear durante un tiempo [ADMIN]""")
							return
					except IndexError:
						conversations[index].notify("""Comandos disponibles:
													   \t\u2022 /noti: Activa o desactiva las notificaciones de tus tweets
													   \t\u2022 /ban: Evita que un usuario pueda twittear [ADMIN]
													   \t\u2022 /timeout: Evita que un usuario pueda twittear durante un tiempo [ADMIN]""")
				else:
					conversations[index].read(msg)

		if typ in ["fav", "rt", "quote", "reply"] and index != None:
			if conversations[index].noti:
				if typ == "fav":
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