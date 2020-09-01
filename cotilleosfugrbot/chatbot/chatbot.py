from . import api_handler as api
from . import conver_handler as conv
from .models import User, Tweet
from .welcomemsg import welcomemsgtext
import logging
import datetime
import requests

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
		try:
			user = User.objects.get(id=int(uid))
			conversations.append(conv.conversation.from_model(user))
			return len(conversations) - 1
		except User.DoesNotExist:
			return None
			

	if typ == "fav":
		tid = jsondata["favorite_events"][0]["favorited_status"]["id"]
		try:
			twt = Tweet.objects.get(id=int(tid))
			uid = twt.user.id
			for c in conversations:
				if int(c.user_id) == uid:
					return index
				index += 1
			conversations.append(conv.conversation.from_model(twt.user))
			return len(conversations) - 1
		except Tweet.DoesNotExist:
			return None

	if typ in ["rt", "quote", "reply"]:
		if typ == "quote":
			tid = jsondata["tweet_create_events"][0]["quoted_status_id"]
			try:
				twt = Tweet.objects.get(id=int(tid))
				uid = twt.user.id
				for c in conversations:
					if int(c.user_id) == uid:
						return index
					index += 1
				conversations.append(conv.conversation.from_model(twt.user))
				return len(conversations) - 1
			except Tweet.DoesNotExist:
				return None
		else:
			try:
				# Retweet
				tid = jsondata["tweet_create_events"][0]["retweeted_status"]["id_str"]
				t_db = Tweet.objects.get(id=int(tid))
				uid = t_db.user.id
				if (str(uid) == api.selfid):
					return -1
				for c in conversations:
					if c.user_id == str(uid):
						return index
					index += 1
				conversations.append(conv.conversation.from_model(t_db.user))
				return len(conversations) - 1
			except Tweet.DoesNotExist:
				return None
			except KeyError:
				try:
					# Respuesta
					replied_user_id = jsondata["tweet_create_events"][0]["in_reply_to_user_id"]
					if replied_user_id == api.selfid:
						tid = jsondata["tweet_create_events"][0]["in_reply_to_status_id"]
						try:
							t_db = Tweet.objects.get(id=tid)
							uid = t_db.user.id
							if (str(uid) == api.selfid):
								return -1
							for c in conversations:
								if c.user_id == str(uid):
									return index
								index += 1
							conversations.append(conv.conversation.from_model(t_db.user))
							return len(conversations) - 1
						except Tweet.DoesNotExist:
							return None
				except KeyError:
					return -1
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
				else:
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
						
						if command[0] == "delete":
							try:
								turl = msg.url()
								tid = int(turl.split("/")[5])
								t_db = Tweet.objects.get(id=tid)
								if (conversations[index].user_id == str(t_db.user.id)) or (conversations[index].isadmin):
									uname = api.getusername(t_db.user.id)[0]
									conversations[index].notify(f"El tweet de @{uname} fue eliminado correctamente", critical=True)
									api.tweet_delete(tid)
								else:
									conversations[index].notify("No tienes permisos para eliminar este tweet", critical=True)
							except api.NoUrlException:
								conversations[index].notify("Uso: /delete <tweet_link>", critical=True)
							except Tweet.DoesNotExist:
								conversations[index].notify("El tweet no está registrado en la base de datos", critical=True)


						elif (command[0] in ["ban", "timeout", "list", "free", "expose"]):
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
										conversations[index].notify("Uso: /ban [link/user] <tweet_link/username>", critical=True)
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
													conversations[index].notify(f"El usuario @{uname} no podrá twittear hasta: {date_string}", critical=True)
												except Tweet.DoesNotExist:
													conversations[index].notify("El tweet no está registrado en la base de datos", critical=True)
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
												conversations[index].notify(f"El usuario @{u} no podrá twittear hasta: {date_string}", critical=True)
											except api.NoidException:
												conversations[index].notify(f"El usuario @{u} no existe", critical=True)
											except User.DoesNotExist:
												p_end = datetime.datetime.utcnow() + datetime.timedelta(days=days)
												u_db = User(id=int(uid), punishment_type="TMO", punishment_end=p_end)
												u_db.save()
												date_string = p_end.strftime("%d/%m/%Y, %H:%M:%S UTC")
												conversations[index].notify(f"El usuario @{u} no podrá twittear hasta: {date_string}", critical=True)
											return
										else:
											raise IndexError
									except IndexError:
										conversations[index].notify("Uso: /timeout [link/user] <tweet_link/username> <días>", critical=True)

								if command[0] == "list":
									banned = User.objects.filter(punishment_type="BAN")
									timed_out = User.objects.filter(punishment_type="TMO").filter(punishment_end__gt=datetime.datetime.now(datetime.timezone.utc))
									ids = [user.id for user in banned] + [user.id for user in timed_out]
									names =  api.getusername(*ids)
									response = "Lista de usuarios castigados:\n\t\u2022 Ban:\n"
									for banned_user in names[:len(banned)]:
										response += f"\t\t\t    - @{banned_user}\n"
									response += "\t\u2022 Timeout:\n"
									for tmo_user_name, tmo_user_db in zip(names[len(banned)::], timed_out):
										tmo_until = tmo_user_db.punishment_end.strftime("%d/%m/%Y, %H:%M:%S UTC")
										response += f"\t\t\t    - @{tmo_user_name}\n\t\t      hasta: {tmo_until}\n"
									conversations[index].notify(response, critical=True)

								if command[0] == "free":
									try:
										uname = command[1]
										try:
											uid = api.getuserid(uname)[0]
											u_db = User.objects.get(id=uid)
											if u_db.punishment_type == "NAN":
												conversations[index].notify(f"El usuario @{uname} no está castigado", critical=True)
											else:
												u_db.punishment_type = "NAN"
												u_db.punishment_end = None
												u_db.save()
												conversations[index].notify(f"Se ha eliminado el castigo al usuario: @{uname}", critical=True)
										except api.NoidException:
											conversations[index].notify(f"El usuario @{uname} no existe", critical=True)
										except User.DoesNotExist:
											conversations[index].notify(f"El usuario @{uname} no está castigado", critical=True)
									except IndexError:
										conversations[index].notify("Uso: /free <username>")

								if command[0] == "expose":
									try:
										turl = msg.url()
										tid = int(turl.split("/")[5])
										t_db = Tweet.objects.get(id=tid)
										uname = api.getusername(t_db.user.id)[0]
										conversations[index].notify(f"El tweet fue publicado por: @{uname}", critical=True)
									except api.NoUrlException:
										conversations[index].notify(f"Uso: /expose <tweet_link>", critical=True)
									except Tweet.DoesNotExist:
										conversations[index].notify("El tweet no está registrado en la base de datos", critical=True)
							else:
								conversations[index].notify("No tienes permisos para hacer uso de este comando", critical=True)
								return
						else:
							if conversations[index].isadmin:
								conversations[index].notify("""Comandos disponibles:
															   \t\u2022 /noti: Activa o desactiva las notificaciones de tus tweets.
															   \t\u2022 /ban: Evita que un usuario pueda twittear.
															   \t\u2022 /timeout: Evita que un usuario pueda twittear durante un tiempo.
															   \t\u2022 /free: Elimina el castigo de un usuario.
															   \t\u2022 /list: Muestra los usuarios castigados.
															   \t\u2022 /delete: Elimina un tweet publicado.
															   \t\u2022 /expose: Muestra el autor de un tweet.""")
							else:
								conversations[index].notify("Comandos disponibles:\n\t\u2022 /noti: Activa o desactiva las notificaciones de tus tweets.\n\t\u2022 /delete: Elimina un tweet publicado por tí.")
							return
					except IndexError:
						if conversations[index].isadmin:
							conversations[index].notify("""Comandos disponibles:
														   \t\u2022 /noti: Activa o desactiva las notificaciones de tus tweets.
														   \t\u2022 /ban: Evita que un usuario pueda twittear.
														   \t\u2022 /timeout: Evita que un usuario pueda twittear durante un tiempo.
														   \t\u2022 /free: Elimina el castigo de un usuario.
														   \t\u2022 /delete: Elimina un tweet publicado.
														   \t\u2022 /expose: Muestra el autor de un tweet.""")
						else:
							conversations[index].notify("Comandos disponibles:\n\t\u2022 /noti: Activa o desactiva las notificaciones de tus tweets.\n\t\u2022 /delete: Elimina un tweet publicado por tí.")
				else:
					conversations[index].read(msg)

		if typ in ["fav", "rt", "quote", "reply"] and index != None:
			if conversations[index].noti:
				if typ == "fav":
					fav = jsondata["favorite_events"][0]
					user = fav["user"]["screen_name"]
					link = "https://twitter.com/" + api.selfscreenname + "/status/" + fav["favorited_status"]["id_str"]
					text = "\u2764 A @" + user + " le ha gustado tu tweet"
					conversations[index].notify(text, link)
				elif typ == "rt":
					rt = jsondata["tweet_create_events"][0]
					user = rt["user"]["screen_name"]
					link = "https://twitter.com/" + api.selfscreenname + "/status/" + rt["retweeted_status"]["id_str"]
					text = "\U0001F504 @" + user + " ha retwiteado tu tweet"
					conversations[index].notify(text, link)
				elif typ == "quote":
					quote = jsondata["tweet_create_events"][0]
					user = quote["user"]["screen_name"]
					link = "https://twitter.com/" + api.selfscreenname + "/status/" + quote["id_str"]
					text = "\U0001F504 @" + user + " ha citado tu tweet"
					conversations[index].notify(text, link)
				elif typ == "reply":
					reply = jsondata["tweet_create_events"][0]
					user = reply["user"]["screen_name"]
					link = "https://twitter.com/" + api.selfscreenname + "/status/" + reply["id_str"]
					text = "\u21A9 @" + user + " ha respondido a tu tweet"
					conversations[index].notify(text, link)

		elif typ == "del":
			tid = jsondata["tweet_delete_events"][0]["status"]["id"]
			t_db = Tweet.objects.filter(id=int(tid))
			t_db.delete()


def cleanconvers():
	for i,c in enumerate(conversations):
		if not c.editingtweets():
			conversations.pop(i)

def cleandatabase():
	default_users = User.objects.filter(punishment_type="NAN").filter(is_admin=False).filter(noti=True)
	for user in default_users:
		if not user.tweet_set.filter(date__lt=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(days=40))):
			user.delete()