import requests
from cotilleosfugrbot.Auths import *
from requests_oauthlib import OAuth1
import os
import sys

#Autenticación
msgauth = OAuth1(consumer, consumer_secret, token, token_secret)

class FullAttachmentException(BaseException):
	def __init__(self, string):
		self.strerr = string

class NoAttachmentException(BaseException):
	def __init__(self, string):
		self.strerr = string

class UnableToTweetException(BaseException):
	def __init__(self, string):
		self.strerr = string

class NoidException(BaseException):
	def __init__(self, string):
		self.strerr = string

class NoUrlException(BaseException):
	def __init__(self, string):
		self.strerr = string

class attachment:
	def __init__(self, path, typ, downloaded=False, url=None):
		self.path = path
		self.type = typ
		switcher = {
			"photo": "image/jpg",
			"video": "video/mp4",
			"animated_gif": "image/gif"
		}
		self.mimetype = switcher[self.type]
		self.size = os.path.getsize(self.path)
		self.downloaded = downloaded
		self.url = url

	def __del__(self):
		if self.downloaded:
			os.remove(self.path)

	@classmethod
	def frommsg(cls, men):
		try:
			if not os.path.isdir("attachments"):
				os.mkdir("attachments")
			#Descarga del archivo
			url = men.data["event"]["message_create"]["message_data"]["attachment"]["media"]["url"]
			p = "attachments/" + men.data["event"]["id"]
			typ = men.data["event"]["message_create"]["message_data"]["attachment"]["media"]["type"]
			switcher = {
				"photo": ".jpg",
				"video": ".mp4",
				"animated_gif": ".mp4"
			}
			extension = switcher[men.data["event"]["message_create"]["message_data"]["attachment"]["media"]["type"]]
			p += extension
			if extension == ".jpg":
				durl = men.data["event"]["message_create"]["message_data"]["attachment"]["media"]["media_url"] + ":large"
			else:
				if typ == "animated_gif":
					durl = men.data["event"]["message_create"]["message_data"]["attachment"]["media"]["video_info"]["variants"][0]["url"]
				else:
					index = 0
					bitrate = 0
					i = 0
					for variant in men.data["event"]["message_create"]["message_data"]["attachment"]["media"]["video_info"]["variants"]:
						if variant["content_type"] == "video/mp4":
							if variant["bitrate"] > bitrate:
								index = i
						i += 1
					durl = men.data["event"]["message_create"]["message_data"]["attachment"]["media"]["video_info"]["variants"][index]["url"]
			with requests.get(durl, auth=msgauth) as r:
				r.raise_for_status()
				with open(p, "wb") as f:
					for chunk in r.iter_content(chunk_size=8192):
						if chunk:
							f.write(chunk)
			return cls(p, typ, downloaded=True, url=url)
		except KeyError:
			raise NoAttachmentException("El mensaje no tiene archivo adjunto")

	def upload(self, destination):
		#Upload media to Twitter to obtain an id
		if self.type == "animated_gif" and self.downloaded:
			uptyp = "video"
		else:
			uptyp = self.type
		#INIT
		if destination is "msg":
			switcher = {
				"photo": "dm_image",
				"video": "dm_video",
				"animated_gif": "dm_gif"
			}
		if destination is "tweet":
			switcher = {
				"photo": "tweet_image",
				"video": "tweet_video",
				"animated_gif": "tweet_gif"
			}

		par = {
			"command": "INIT",
			"total_bytes": self.size,
			"media_type": self.mimetype,
			"media_category": switcher[uptyp]
		}
		r = requests.post("https://upload.twitter.com/1.1/media/upload.json", auth=msgauth, data=par)
		r.raise_for_status()
		m_id = r.json()["media_id"]
		#APPEND
		segment_id = 0
		bytes_sent = 0
		f = open(self.path, "rb")
		while bytes_sent < self.size:
			chunk = f.read(4*1024*1024)
			par = {
				"command": "APPEND",
				"media_id": m_id,
				"segment_index": segment_id
			}
			fil = {
				"media": chunk
			}
			r = requests.post("https://upload.twitter.com/1.1/media/upload.json", auth=msgauth, files=fil, data=par)
			r.raise_for_status()
			segment_id += 1
			bytes_sent = f.tell()
		#FINALIZE
		par = {
			"command": "FINALIZE",
			"media_id": m_id
		}
		r = requests.post("https://upload.twitter.com/1.1/media/upload.json", auth=msgauth, data=par)
		r.raise_for_status()
		return (m_id, switcher[self.type])


class msg:
	def __init__(self, data):
		self.data = {"event": data}
		self.welcomemessageid = None

	@classmethod
	def create(cls, r_id, text):
		data = {
			"type": "message_create",
			"message_create": {
				"target": {
					"recipient_id": str(r_id)
				},
				"message_data": {
					"text": text,
					"quick_reply": None,
					"attachment": None
				}
			}
		}
		return cls(data)

	def text(self): 
		try:
			txt = self.data["event"]["message_create"]["message_data"]["text"]
			for el in self.data["event"]["message_create"]["message_data"]["entities"]["urls"]:
				if el["expanded_url"].split("/")[2] == "twitter.com":
					txt = txt.replace(el["url"], "")
			return txt
		except KeyError:
			return txt

	def rawtext(self):
		return self.data["event"]["message_create"]["message_data"]["text"]

	def chtext(self, text): self.data["event"]["message_create"]["message_data"]["text"] = text
	def id(self): 
		try:
			return self.data["event"]["id"]
		except KeyError:
			raise NoidException("Sólo se conoce los id de los mensajes descargados")

	def sid(self):
		try:
			return self.data["event"]["message_create"]["sender_id"]
		except KeyError:
			raise NoidException("Sólo los mensajes recibidos contienen id del emisor")

	def rid(self): return self.data["event"]["message_create"]["target"]["recipient_id"]
	def chrid(self, nid): self.data["event"]["message_create"]["target"]["recipient_id"] = nid
	def url(self):
		try:
			res = None
			for el in self.data["event"]["message_create"]["message_data"]["entities"]["urls"]:
				try:
					typ = el["expanded_url"].split("/")[4]
				except IndexError:
					typ = None
				if typ == "status":
					res = el["expanded_url"]
					break
			if res == None:
				raise KeyError
			else:
				return res
		except KeyError:
			raise NoUrlException("Este mensaje no contiene url de tweet citado")
	def post(self): 
		try:
			r = requests.post("https://api.twitter.com/1.1/direct_messages/events/new.json", auth=msgauth, json=self.data)
			r.raise_for_status()
		except requests.HTTPError: 
			print(r.json()["errors"][0]["message"], file=sys.stderr)
	def attach(self, attachm):
		response = attachm.upload("msg")
		self.data["event"]["message_create"]["message_data"]["attachment"] = {
			"type": "media",
			"media": {
				"id": response[0],
				"type": response[1]
			}
		}

	def rmattach(self):
		self.data["event"]["message_create"]["message_data"]["attachment"] = None

	def attachtype(self):
		try:
			return self.data["event"]["message_create"]["message_data"]["attachment"]["media"]["type"]
		except KeyError:
			raise NoAttachmentException("El mensaje no tiene archivo adjunto")
	
	def addquickreply(self, title, description=None, metadata=None):
		if self.data["event"]["message_create"]["message_data"]["quick_reply"] is None:
			self.data["event"]["message_create"]["message_data"]["quick_reply"] = {
				"type": "options",
				"options": [
					{
						"label": title,
						"description": description,
						"metadata": metadata
					}
				]
			}
		else: 
			self.data["event"]["message_create"]["message_data"]["quick_reply"]["options"].append({"label": title, "description": description, "metadata": metadata})

	def quickreplyresponse(self):
		if "quick_reply_response" in self.data["event"]["message_create"]["message_data"].keys():
			try:
				return self.data["event"]["message_create"]["message_data"]["quick_reply_response"]["metadata"]
			except KeyError:
				return None
		else: return None

	def getquickreply(self, index=-1):
		if index is -1:
			return self.data["event"]["message_create"]["message_data"]["quick_reply"]["options"]
		else:
			return self.data["event"]["message_create"]["message_data"]["quick_reply"]["options"][index]

	def rmquickreply(self, index=-1):
		if index is -1:
			self.data["event"]["message_create"]["message_data"]["quick_reply"] = None
		else:
			try:
				del self.data["event"]["message_create"]["message_data"]["quick_reply"]["options"][index]
			except KeyError:
				raise NoAttachmentException("No existe la respuesta rápida " + str(index))

	def setaswelcomemsg(self, name=None):
		data = {
			"welcome_message": {
				"name": name,
				"message_data": self.data["event"]["message_create"]["message_data"]
			}
		}
		r = requests.post("https://api.twitter.com/1.1/direct_messages/welcome_messages/new.json", auth=msgauth, json=data)
		r.raise_for_status()
		self.welcomemessageid = r.json()["welcome_message"]["id"]
		data = {
			"welcome_message_rule": {
				"welcome_message_id": self.welcomemessageid
			}
		}
		r = requests.post("https://api.twitter.com/1.1/direct_messages/welcome_messages/rules/new.json", auth=msgauth, json=data)
		r.raise_for_status()
		self.ruleid = r.json()["welcome_message_rule"]["id"]

class tweet:
	def __init__(self, data):
		self.data = data

	@classmethod
	def create(cls, text):
		data = {
			"status": text,
			"media_ids": None,
			"attachment_url": None,
			"entities": None,
			"in_reply_to_status_id": None,
			"auto_populate_reply_metadata": False
		}
		return cls(data)

	def text(self):
		try:
			return self.data["status"]
		except KeyError:
			return self.data["text"]

	def id(self):
		try:
			return self.data["id"]
		except KeyError:
			raise NoidException("Sólo se conoce el id de los tweets descargados")

	def post(self):
		try:
			r = requests.post("https://api.twitter.com/1.1/statuses/update.json", auth=msgauth, params=self.data)
			r.raise_for_status()
			return r.json()["id"]
		except requests.HTTPError as e:
			if e.args[0][0:3] == "403":
				raise UnableToTweetException("No es posible twitear los tweets descargados")
			else: 
				print(r.text)


	def attach(self, attachm):
		gid = attachm.upload("tweet")[0]
		if type(self.data["media_ids"]) is list:
			if len(self.data["media_ids"]) == 4:
				raise FullAttachmentException("No se pueden adjuntar más de 4 fotos")
			if attachm.type != "photo":
				raise FullAttachmentException("No se puden adjuntar fotos juntos a un vídeo/gif")
			else:
				self.data["media_ids"].append(gid)
		if type(self.data["media_ids"]) is int:
			raise FullAttachmentException("Únicamente se puede ajuntar un vídeo/gif")
		if (self.data["media_ids"] is None) and (attachm.type == "photo"):
			self.data["media_ids"] = [gid]
		if (self.data["media_ids"] is None) and not (attachm.type == "photo"):
			self.data["media_ids"] = gid

	def rmattach(self, index=-1):
		if type(self.data["media_ids"]) is list:
			if index is -1:
				self.data["media_ids"] = None
			else:
				try:
					del self.data["media_ids"][index]
				except KeyError:
					raise NoAttachmentException("No existe el archivo adjunto " + str(index))
		else:
			self.data["media_ids"] = None

	def numattachments(self):
		if self.data["media_ids"] == None:
			return 0
		else:
			try:
				return len(self.data["media_ids"])
			except TypeError:
				return 1

	def quote(self, link=None):
		if link:
			self.data["attachment_url"] = link
		else:
			return self.data["attachment_url"]

	def rmquote(self):
		self.data["attachment_url"] = None

	def inreplyto(self, t_id):
		self.data["in_reply_to_status_id"] = t_id
		self.data["auto_populate_reply_metadata"] = True

#Func for obtaining messages
def getmsg(num):
	if(num > 50): num = 50
	if(num == 1):
		r = requests.get("https://api.twitter.com/1.1/direct_messages/events/list.json", auth=msgauth, params={"count":num})
		r.raise_for_status()
		return msg(r.json()["events"][0])
	if(num <= 0): return []
	#Call the api for messages
	r = requests.get("https://api.twitter.com/1.1/direct_messages/events/list.json", auth=msgauth, params={"count":num})
	r.raise_for_status()
	response = [msg(event) for event in r.json()["events"]]
	return response

#Func for obtaining tweets from id or url
def gettweet(t_id):
	if (type(t_id) is str):
		t_id = t_id.split("/")[5]
	r = requests.get("https://api.twitter.com/1.1/statuses/show.json", auth=msgauth, params={"id": t_id})
	r.raise_for_status()
	return tweet(r.json())

#Returns authenticated user's id
def getselfid():
	r = requests.get("https://api.twitter.com/1.1/account/verify_credentials.json", auth=msgauth)
	r.raise_for_status()
	return r.json()["id"]

#Returns authenticated user's screen name (@)
def getselfscreenname():
	r = requests.get("https://api.twitter.com/1.1/account/verify_credentials.json", auth=msgauth)
	r.raise_for_status()
	return r.json()["screen_name"]

#Function for obtaining user id from screen name
def getuserid(*screen_names):
	par = {"screen_name": screen_names}
	r = requests.get("https://api.twitter.com/1.1/users/lookup.json", auth=msgauth, params=par)
	r.raise_for_status()
	return [user["id_str"] for user in r.json()]

#Function for obtaining user_name from id
def getusername(*ids):
	par = {"user_id": ids}
	r = requests.get("https://api.twitter.com/1.1/users/lookup.json", auth=msgauth, params=par)
	r.raise_for_status()
	return [user["screen_name"] for user in r.json()]

try:
	selfid = getselfid()
	selfscreenname = getselfscreenname()
except requests.HTTPError:
	selfid = None
	selfscreenname = None