import api_handler as api
import datetime
import threading
from time import sleep
from config import MAX_TWEETS_PER_HOUR, SCORE_ZERO_ERROR
from spamfilter import is_inapropiate

class ConverError(BaseException):
	def __init__(self, string, critical=False):
		self.strerr = string
		self.critical = critical

class conversation:
	def __init__(self, user_id, tweets=[], creationdate=datetime.datetime.utcnow(), punishment=None, isadmin=False):
		self.user_id = user_id
		self.tweets = tweets
		self.tweetstopost = []
		self.pendingnot = []
		self.currtweettext = ""
		self.currtweetquote = ""
		self.currtweetattachments = []
		self.finalattachments = []
		self.taskqueue = []
		self.thread = threading.Thread(target=self.queue)
		self.punishment = punishment
		self.creationdate = creationdate
		self.isadmin = isadmin

	@classmethod
	def from_model(cls, model):
		model_tweets = model.tweets
		tweets = [(tweet.id, tweet.creation_date) for tweet in model_tweets]
		if model.punishment_type == "timeout":
			punishment = ("timeout", model.punishment_end)
		elif model.punishment_type == "ban":
			punishment = ("ban", None)
		else:
			punishment = None
		return cls(str(model.id), tweets=tweets, creationdate=model.creation_date, punishment=punishment, isadmin=model.admin)

	def queue(self):
		while not len(self.taskqueue) == 0:
			task = self.taskqueue.pop(0)
			task()

	def addsendbutton(self):
		if len(self.tweetstopost) == 0:
			self.response.addquickreply("Publicar tweet",
			description="¡Publica tu tweet!",
			metadata="Enviar tweet")
		else:
			self.response.addquickreply("Publicar hilo",
			description="¡Publica tu hilo!",
			metadata="Enviar tweet")

	def send(self):
		spamming = False
		try:
			delta = datetime.datetime.utcnow() - self.tweets[len(self.tweets)-MAX_TWEETS_PER_HOUR-1][1]
			if delta < datetime.timedelta(hours=1):
				spamming = True
		except IndexError:
			pass
		if spamming:
			timefortweeting = self.tweets[len(self.tweets)-6][1] + datetime.timedelta(hours=1)
			raise ConverError("Has superado el límite de 5 tweets por hora, podrás volver a twittear a las " + (timefortweeting + datetime.timedelta(hours=2)).strftime("%X"))
		if self.punishment:
			if self.punishment[0] == "timeout":
				if self.punishment[1] < datetime.datetime.utcnow():
					self.punishment = None
				else:
					end = self.punishment[1].strftime("%H:%M:%S %d/%m/%Y UTC")
					raise ConverError("Has recibido un castigo por comportamiento inapropiado, no podrás twittear hasta: " + end, critical=True)
			else:
				raise ConverError("Has recibido el mayor castigo por comportamiento inapropiado, no podrás volver a twittear nunca más", critical=True)
		#Check if there is a current tweet on editing
		self.creationdate = datetime.datetime.utcnow()
		conditions = [
			self.currtweettext == "",
			self.currtweetattachments == [],
			self.currtweetquote == ""
		]
		if not all(conditions):
			self.endtweetedit()
		if len(self.tweetstopost) == 1:
			self.response = api.msg.create(self.user_id, "¡Tweet enviado!")
		else:
			self.response = api.msg.create(self.user_id, "¡Hilo enviado!")
		self.response.post()
		for i,tweet in enumerate(self.tweetstopost):
			if i != 0:
				tweet.inreplyto(self.tweets[len(self.tweets)-1])
			self.tweets.append((tweet.post(), datetime.datetime.utcnow()))
		self.tweetstopost = []
		self.currtweetquote = ""
		self.currtweetattachments = []
		self.currtweettext = ""
		self.finalattachments = []

	def addcancelbutton(self):
		self.response.addquickreply("Cancelar",
		description="Borrar el tweet o el hilo",
		metadata="Cancelar")

	def cancel(self):
		if len(self.tweetstopost) == 0:
			self.response = api.msg.create(self.user_id, "Tweet cancelado")
		else:
			self.response = api.msg.create(self.user_id, "Hilo cancelado")
		self.response.post()
		self.tweetstopost = []
		self.currtweetquote = ""
		self.currtweetattachments = []
		self.currtweettext = ""
		self.finalattachments = []

	def removeattachmentbutton(self):
		self.response.addquickreply("Eliminar último archivo adjunto",
		description="No se adjuntará en el tweet",
		metadata="Eliminar último archivo adjunto")

	def removeattachment(self):
		attachment = self.currtweetattachments.pop()
		self.response = api.msg.create(self.user_id, "Se ha eliminado este archivo adjunto")
		self.response.attach(attachment)
		self.response.post()

	def removequotebutton(self):
		self.response.addquickreply("Eliminar tweet citado",
		description="No se citará en el tweet final",
		metadata="Eliminar tweet citado")

	def removequote(self):
		quote = self.currtweetquote
		self.currtweetquote = ""
		self.response = api.msg.create(self.user_id, "Se ha dejado de citar al tweet mostrado " + quote)
		self.response.post()

	def addtweetbutton(self):
		self.response.addquickreply("Añadir tweet al hilo",
		description="Crea un nuevo tweet para formar un hilo",
		metadata="Añadir tweet al hilo")

	def addtweet(self):
		spamming = False
		try:
			delta = datetime.datetime.utcnow() - self.tweets[len(self.tweets)-MAX_TWEETS_PER_HOUR-1][1]
			if delta < datetime.timedelta(hours=1):
				spamming = True
		except IndexError:
			pass
		if spamming:
			timefortweeting = self.tweets[len(self.tweets)-6][1] + datetime.timedelta(hours=1)
			raise ConverError("Has superado el límite de 5 tweets por hora, podrás añadir otro tweet al hilo a las " + (timefortweeting + datetime.timedelta(hours=2)).strftime("%X"))
		else:
			self.endtweetedit()
			self.response = api.msg.create(self.user_id, "Envía texto, archivo adjuntos o links de tweets para el nuevo tweet del hilo")
			self.removetweetbutton()
			self.addsendbutton()
			self.addcancelbutton()
			self.response.post()

	def removetweetbutton(self):
		self.response.addquickreply("Eliminar último tweet del hilo",
		description="Elimina el tweet que estás editando",
		metadata="Eliminar último tweet del hilo")

	def removetweet(self):
		lasttweet = self.tweetstopost.pop()
		self.currtweettext = lasttweet.text()
		self.currtweetattachments = []
		for i in range(lasttweet.numattachments()):
			self.currtweetattachments.insert(0, self.finalattachments.pop())
		self.currtweetquote = lasttweet.getquote()
		if self.currtweetquote == None: self.currtweetquote = ""

	def endtweetedit(self):
		text_rate = is_inapropiate(self.currtweettext)
		if len(self.currtweettext) > 280:
			raise ConverError(f"El tweet contiene más de 280 carácteres ({len(self.currtweettext)})")
		elif (self.currtweettext == "" or self.currtweettext.isspace()) and len(self.currtweetattachments)==0:
			raise ConverError("Sólo se permiten enviar tweets sin texto si estos contienen archivos adjuntos")
		elif text_rate[0]:
			raise ConverError("El tweet que deseas enviar es inapropiado")
		elif text_rate[1] == 0 and int(SCORE_ZERO_ERROR):
			raise ConverError("El texto no tiene sentido")
		else:
			tweet = api.tweet.create(self.currtweettext)
			for attachment in self.currtweetattachments:
				self.finalattachments.append(attachment)
				tweet.attach(attachment)
			if self.currtweetquote != "":
				tweet.quote(self.currtweetquote)
			self.tweetstopost.append(tweet)
			self.currtweettext = ""
			self.currtweetattachments = []
			self.currtweetquote = ""

	def read(self, msg):
		try:
			if msg.quickreplyresponse() == None:
				#Text
				if not (msg.text().isspace() or msg.text() == ""):
					self.currtweettext = msg.text()
				#Attachments
				try:
					attachment = api.attachment.frommsg(msg)
					if len(self.currtweetattachments) >= 1 and len(self.currtweetattachments) < 4:
						if self.currtweetattachments[0].type == "photo" and attachment.type == "photo":
							self.currtweetattachments.append(attachment)
						elif self.currtweetattachments[0].type != "photo" and attachment.type != "photo" and len(self.currtweetattachments) == 1:
							raise ConverError("Únicamente se puede adjuntar un vídeo/gif")
						else:
							raise ConverError("No se pueden adjuntar vídeos/gifs junto a fotos")
					elif len(self.currtweetattachments) == 4:
						raise ConverError("No es posible adjuntar más de 4 fotos")
					else:
						self.currtweetattachments.append(attachment)
				except api.NoAttachmentException:
					pass
				#Quote
				try:
					self.currtweetquote = msg.url()
				except api.NoUrlException:
					pass
				#Response
				self.respond()
			elif msg.quickreplyresponse() == "Eliminar último archivo adjunto":
				self.removeattachment()
				self.respond()
			elif msg.quickreplyresponse() == "Eliminar tweet citado":
				self.removequote()
				self.respond()
			elif msg.quickreplyresponse() == "Cancelar":
				self.cancel()
				for noti in self.pendingnot:
					noti.post()
			elif msg.quickreplyresponse() == "Añadir tweet al hilo":
				self.taskqueue.append(self.addtweet())
			elif msg.quickreplyresponse() == "Eliminar último tweet del hilo":
				self.removetweet()
				self.respond()
			elif msg.quickreplyresponse() == "Enviar tweet":
				self.taskqueue.append(self.send())
				for noti in self.pendingnot:
					noti.post()
				return True
		except ConverError as e:
			self.respond(errortext=e.strerr)
			if e.critical:
				self.cancel()
				return True

	def respond(self, errortext=""):
		responsetext = "Se publicará el siguiente "
		if len(self.tweetstopost) == 0:
			responsetext += "tweet:\n"
		else:
			responsetext += "hilo:\n"
		shownattachments = 0
		for tweet in self.tweetstopost:
			if tweet.text() == "":
				responsetext += "**Tweet sin texto**\n"
			else:
				responsetext += tweet.text() + "\n"
			numattachments = tweet.numattachments()
			if numattachments == 1:
				if self.finalattachments[shownattachments].type == "photo":
					responsetext += "Con 1 foto adjunta\n"
				elif self.finalattachments[shownattachments].type == "video":
					responsetext += "Con 1 vídeo adjunto\n"
				else:
					responsetext += "Con 1 gif adjunto\n"
				shownattachments += 1
			elif numattachments > 1:
				responsetext += "Con " + numattachments + " fotos adjuntas"
				shownattachments += numattachments
			if tweet.getquote() != None:
				responsetext += "Citando 1 tweet\n"
			responsetext += "---------------///---------------\n"

		if self.currtweettext == "":
			responsetext += "**Tweet sin texto**\n"
		else:
			responsetext += self.currtweettext + "\n"
		if len(self.currtweetattachments) > 1:
			responsetext += "Con " + str(len(self.currtweetattachments)) + " fotos adjuntas\n"
		elif len(self.currtweetattachments) == 1:
			if self.currtweetattachments[0].type == "video":
				responsetext += "Con 1 vídeo adjunto\n"
			elif self.currtweetattachments[0].type == "animated_gif":
				responsetext += "Con 1 gif adjunto\n"
			else:
				responsetext += "Con 1 foto adjunta\n"
		if self.currtweetquote != "":
			if errortext != "":
				responsetext += "Citando al tweet mostrado\n\nERROR: " + errortext
			else:
				responsetext += "Citando al tweet mostrado"
			self.response = api.msg.create(self.user_id, responsetext)
			self.response.post()
			self.response = api.msg.create(self.user_id, self.currtweetquote)
			if len(self.tweetstopost) < 4:
				self.addtweetbutton()
			if len(self.tweetstopost) > 0:
				self.removetweetbutton()
			if len(self.currtweetattachments) > 0:
				self.removeattachmentbutton()
			self.removequotebutton()
			self.addsendbutton()
			self.addcancelbutton()
			self.response.post()
		else:
			if errortext != "":
				responsetext += "\n\nERROR: " + errortext
			self.response = api.msg.create(self.user_id, responsetext)
			if len(self.tweetstopost) < 4:
				self.addtweetbutton()
			if len(self.tweetstopost) > 0:
				self.removetweetbutton()
			if len(self.currtweetattachments) > 0:
				self.removeattachmentbutton()
			self.addsendbutton()
			self.addcancelbutton()
			self.response.post()

	def notify(self, text, link=None, critical=False):
		noti = api.msg.create(self.user_id, text)
		notilink = api.msg.create(self.user_id, link)
		if not self.editingtweets() or critical:
			if link:
				notilink.post()
			noti.post()
		else:
			if link:
				self.pendingnot.append(notilink)
			self.pendingnot.append(noti)

	def editingtweets(self):
		conditions = [
		self.currtweettext == "",
		self.currtweetattachments == [],
		self.currtweetquote == "",
		self.tweetstopost == []
		]
		return not all(conditions)

	def timeout(self,days):
		end_punishment = datetime.datetime.utcnow() + datetime.timedelta(days=days)
		self.punishment = "timeout", end_punishment

	def ban(self):
		self.punishment = "ban", None

	def forgive(self):
		self.punishment = None