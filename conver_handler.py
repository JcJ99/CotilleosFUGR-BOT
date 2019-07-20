import api_handler as api
import datetime
import threading
from time import sleep

class conversation:
	def __init__(self, user_id):
		self.user_id = user_id
		self.tweets = []
		self.attachments = []
		self.status = "000"
		self.response = None
		self.tweettext = ""
		self.quote = ""
		self.pendingnot = []

	def addattachmentbutton(self):
		self.response.addquickreply("Adjuntar una foto, vídeo o gif",
		description="Adjunta un archivo que aparecerá en el tweet",
		metadata="Adjuntar una foto, vídeo o gif")

	def addattachment(self, msg):
		try:
			self.attachments.append(api.attachment.frommsg(msg))
			if self.attachments[0].type == "photo":
				if self.tweettext == "":
					self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con 1 foto citando al tweet mostrado " + self.quote)
					self.addphotobutton()
					self.removeattachmentbutton()
					self.removequotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "011"
				else:
					if self.quote == "":
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 foto adjunta")
						self.addphotobutton()
						self.removeattachmentbutton()
						self.addquotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "110"
					else:
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 foto adjunta\nCitando al tweet mostrado " + self.quote)
						self.addphotobutton()
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "111"
			elif self.attachments[0].type == "video":
				if self.tweettext == "":
					self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con 1 vídeo citando al tweet mostrado " + self.quote)
					self.removeattachmentbutton()
					self.removequotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "051"
				else:
					if self.quote == "":
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 vídeo adjunto")
						self.removeattachmentbutton()
						self.addquotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "150"
					else:
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 vídeo adjunto\nCitando al tweet mostrado " + self.quote)
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "151"
			elif self.attachments[0].type == "animated_gif":
				if self.tweettext == "":
					self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con 1 gif citando al tweet mostrado " + self.quote)
					self.removeattachmentbutton()
					self.removequotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "061"
				else:
					if self.quote == "":
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 gif adjunto")
						self.removeattachmentbutton()
						self.addquotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "160"
					else:
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 gif adjunto\nCitando al tweet mostrado " + self.quote)
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "161"
		except api.NoAttachmentException:
			if self.response.text().split()[0] == "ERROR:":
				responsetext = self.response.text().split("\n\n")[1]
				self.response.chtext("ERROR: Adjunta una foto/vídeo/gif en el mensaje para que aparezca en el tweet\n\n" + responsetext)
			else:
				self.response.chtext("ERROR: Adjunta una foto/vídeo/gif en el mensaje para que aparezca en el tweet\n\n" + self.response.text())


	def addphotobutton(self):
		self.response.addquickreply("Adjuntar una foto",
		description="Adjunta una foto para añadirla al tweet",
		metadata="Adjuntar una foto")

	def addphoto(self, msg):
		try:
			attachment = api.attachment.frommsg(msg)
			if attachment.type != "photo":
				if self.response.text().split()[0] == "ERROR:":
					responsetext = self.response.text().split("\n\n")[1]
					self.response.chtext("ERROR: No es posible adjuntar vídeos/gifs junto a fotos\n\n" + self.responsetext)
				else:
					self.response.chtext("ERROR: No es posible adjuntar vídeos/gifs junto a fotos\n\n" + self.response.text())
			else:
				self.attachments.append(attachment)
				if self.quote == "":
					if self.tweettext == "":
						self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con " + str(len(self.attachments)) + " fotos adjuntas")
						if len(self.attachments) == 4:
							self.removeattachmentbutton()
							self.addquotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						else:
							self.addphotobutton()
							self.removeattachmentbutton()
							self.addquotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						self.status = "0" + str(len(self.attachments)) + "0"
					else:
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon " + str(len(self.attachments)) + " fotos adjuntas")
						if len(self.attachments) == 4:
							self.removeattachmentbutton()
							self.addquotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						else:
							self.addphotobutton()
							self.removeattachmentbutton()
							self.addquotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						self.status = "1" + str(len(self.attachments)) + "0"
				else:
					if self.tweettext == "":
						self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con " + str(len(self.attachments)) + " fotos adjuntas citando al tweet mostrado " + self.quote)
						if len(self.attachments) == 4:
							self.removeattachmentbutton()
							self.removequotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						else:
							self.addphotobutton()
							self.removeattachmentbutton()
							self.removequotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						self.status = "0" + str(len(self.attachments)) + "1"
					else:
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon " + str(len(self.attachments)) + " fotos adjuntas\nCitando al tweet mostrado " + self.quote)
						if len(self.attachments) == 4:
							self.removeattachmentbutton()
							self.removequotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						else:
							self.addphotobutton()
							self.removeattachmentbutton()
							self.removequotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						self.status = "1" + str(len(self.attachments)) + "1"
		except api.NoAttachmentException:
			if self.response.text().split()[0] == "ERROR:":
				responsetext = self.response.text().split("\n\n")[1]
				self.response.chtext("ERROR: Adjunta una foto en el mensaje para que aparezca en el tweet\n\n" + responsetext)
			else:
				self.response.chtext("ERROR: Adjunta una foto en el mensaje para que aparezca en el tweet\n\n" + self.response.text())

	def addsendbutton(self):
		self.response.addquickreply("Enviar tweet",
		description="¡Publica tu tweet!",
		metadata="Enviar tweet")

	def send(self):
		length = len(self.tweettext)
		spamming = False
		try:
			delta = datetime.datetime.now() - self.tweets[len(self.tweets)-7][1]
			if delta < datetime.timedelta(hours=1):
				spamming = True
		except IndexError:
			pass
		if length > 280:
			if self.response.text().split()[0] == "ERROR:":
				responsetext = self.response.text().split("\n\n")[1]
				self.response.chtext(f"ERROR: El tweet contiene más de 280 carácteres ({length})\n\n" + responsetext)
			else:
				self.response.chtext(f"ERROR: El tweet contiene más de 280 carácteres ({length})\n\n" + self.response.text())
		elif spamming:
			timefortweeting = self.tweets[len(self.tweets)-6][1] + datetime.timedelta(hours=1)
			if self.response.text().split()[0] == "ERROR:":
				responsetext = self.response.text().split("\n\n")[1]
				self.response.chtext("ERROR: Has superado el límite de 5 tweets por hora, podrás volver a twittear a las " + timefortweeting.strftime("%X") + "\n\n" + responsetext)
			else:
				self.response.chtext("ERROR: Has superado el límite de 5 tweets por hora, podrás volver a twittear a las " + timefortweeting.strftime("%X") + "\n\n" + self.response.text())
		else:
			thread = threading.Thread(target=self.tweetpost)
			thread.start()
			self.attachments = []
			self.tweettext = ""
			self.quote = ""
			self.status = "000"
			self.response = api.msg.create(self.user_id, "¡Tweet publicado!")


	def addquotebutton(self):
		self.response.addquickreply("Citar tweet",
		description="Envía el link de un tweet para citarlo (No uses este botón)",
		metadata="Citar tweet")

	def addquote(self):
		if self.response.text().split()[0] == "ERROR:":
			responsetext = self.response.text().split("\n\n")[1]
			self.response.chtext("ERROR: TE HE DICHO QUE NO PULSES EL BOTÓN. Para citar un tweet necesito el link, si pulsas el botón el link se sustituye por el nombre del botón. Para enviar el link del tweet citado usa el botón de enviar que usarías para mandarle un dm a tu crush\n\n" + responsetext)
		else:
			self.response.chtext("ERROR: TE HE DICHO QUE NO PULSES EL BOTÓN. Para citar un tweet necesito el link, si pulsas el botón el link se sustituye por el nombre del botón. Para enviar el link del tweet citado usa el botón de enviar que usarías para mandarle un dm a tu crush\n\n" + self.response.text())

	def addcancelbutton(self):
		self.response.addquickreply("Cancelar",
		description="No enviar tweet",
		metadata="Cancelar")

	def cancel(self):
		self.response = api.msg.create(self.user_id, "Tweet cancelado")
		self.tweettext = ""
		self.quote = ""
		self.attachments = []
		self.status = "000"

	def removeattachmentbutton(self):
		self.response.addquickreply("Eliminar último archivo adjunto",
		description="No se adjuntará en el tweet",
		metadata="Eliminar último archivo adjunto")

	def removeattachment(self):
		if self.status[1] in ["1","5","6"]:
			attachment = self.attachments.pop()
			if self.tweettext == "":
				if self.quote == "":
					self.response = api.msg.create(self.user_id, "Tweet cancelado al eliminar el archivo mostrado y no contar con texto ni tweet citado")
					self.response.attach(attachment)
					self.status = "000"
				else:
					self.response = api.msg.create(self.user_id, "Se ha eliminado este archivo adjunto")
					self.response.attach(attachment)
					self.response.post()
					self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto citando al tweet mostrado " + self.quote)
					self.addattachmentbutton()
					self.removequotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "001"
			else:
				if self.quote == "":
					self.response = api.msg.create(self.user_id, "Se ha eliminado este archivo adjunto")
					self.response.attach(attachment)
					self.response.post()
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext)
					self.addattachmentbutton()
					self.addquotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "100"
				else:
					self.response = api.msg.create(self.user_id, "Se ha eliminado este archivo adjunto")
					self.response.attach(attachment)
					self.response.post()
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweetext + "\nCitando al tweet mostrado " + self.quote)
					self.addattachmentbutton()
					self.removequotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "101"
		else:
			attachment = self.attachments.pop()
			self.response = api.msg.create(self.user_id, "Se ha eliminado este archivo adjunto")
			self.response.attach(attachment)
			self.response.post()
			if self.tweettext == "":
				if self.quote == "":
					self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con " + str(len(self.attachments)) + " fotos adjuntas")
					self.addphotobutton()
					self.removeattachmentbutton()
					self.addquotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "0" + str(len(self.attachments)) + "0"
				else:
					self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con " + str(len(self.attachments)) + " fotos adjuntas citando al tweet mostrado " + self.quote)
					self.addphotobutton()
					self.removeattachmentbutton()
					self.removequotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "0" + str(len(self.attachments)) + "1"
			else:
				if self.quote == "":
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon " + str(len(self.attachments)) + " fotos adjuntas")
					self.addphotobutton()
					self.removeattachmentbutton()
					self.addquotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "1" + str(len(self.attachments)) +  "0"
				else:
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon " + str(len(self.attachments)) + " fotos adjuntas citando al tweet mostrado " + self.quote)
					self.addphotobutton()
					self.removeattachmentbutton()
					self.removequotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "1" + str(len(self.attachments)) + "1"

	def removequotebutton(self):
		self.response.addquickreply("Eliminar tweet citado",
		description="No se citará en el tweet final",
		metadata="Eliminar tweet citado")

	def removequote(self):
		quote = self.quote
		self.quote = ""
		self.response = api.msg.create(self.user_id, "Se ha eliminado el tweet citado motrado " + quote)
		self.response.post()
		if self.status[1] == "0":
			if self.tweettext == "":
				self.response = api.msg.create(self.user_id, "Tweet cancelado al eliminar el tweet citado y no contar con texto ni archivos adjuntos")
				self.status = "000"
			else:
				self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext)
				self.addattachmentbutton()
				self.addquotebutton()
				self.addsendbutton()
				self.addcancelbutton()
				self.status = "100"
		elif self.status[1] in ["1", "2", "3", "4"]:
			if self.tweettext == "":
				if self.status[1] == "1":
					self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con 1 foto adjunta")
				else:
					self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con " + str(len(self.attachments)) + " fotos adjuntas")
				if len(self.attachments) == 4:
					self.removeattachmentbutton()
					self.addquotebutton()
					self.addsendbutton()
					self.addcancelbutton()
				else:
					self.addphotobutton()
					self.removeattachmentbutton()
					self.addquotebutton()
					self.addsendbutton()
					self.addcancelbutton()
				self.status = "0" + str(len(self.attachments)) + "0"
			else:
				if self.status[1] == "1":
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 foto adjunta")
				else:
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon " + str(len(self.attachments)) + " fotos adjuntas")
				if len(self.attachments) == 4:
					self.removeattachmentbutton()
					self.addquotebutton()
					self.addsendbutton()
					self.addcancelbutton()
				else:
					self.addphotobutton()
					self.removeattachmentbutton()
					self.addquotebutton()
					self.addsendbutton()
					self.addcancelbutton()
				self.status = "0" + str(len(self.attachments)) + "0"
		elif self.status[1] == "5":
			if self.tweettext == "":
				self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con 1 vídeo adjunto")
				self.addattachmentbutton()
				self.addquotebutton()
				self.addsendbutton()
				self.addcancelbutton()
				self.status = "050"
			else:
				self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 vídeo adjunto")
				self.addattachmentbutton()
				self.addquotebutton()
				self.addsendbutton()
				self.addcancelbutton()
				self.status = "150"
		elif self.status[1] == "6":
			if self.tweettext == "":
				self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con 1 vídeo adjunto")
				self.addattachmentbutton()
				self.addquotebutton()
				self.addsendbutton()
				self.addcancelbutton()
				self.status = "060"
			else:
				self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 gif adjunto")
				self.addattachmentbutton()
				self.addquotebutton()
				self.addsendbutton()
				self.addcancelbutton()
				self.status = "160"

	def status000(self, msg):
		try:
			self.attachments.append(api.attachment.frommsg(msg))
			self.creationdate = datetime.datetime.now()
			try:
				quote = msg.url()
			except api.NoUrlException:
				quote = None
			if self.attachments[0].type == "photo":
				if quote == None:
					if msg.text() == "" or msg.text().isspace():
						self.response = msg.create(self.user_id, "Se publicará un tweet sin texto con una foto")
						self.addphotobutton()
						self.addquotebutton()
						self.removeattachmentbutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "010"
					else:
						self.response = msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + msg.text() + "\nCon 1 foto adjunta")
						self.tweettext = msg.text()
						self.addphotobutton()
						self.addquotebutton()
						self.removeattachmentbutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "110"
				else:
					if msg.text().isspace():
						self.response = msg.create(self.user_id, "Se publicará un tweet sin texto con 1 foto citando al tweet mostrado " + quote)
						self.addphotobutton()
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "011"
					else:
						self.response = msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + msg.text() + "\nCon 1 foto adjunta\nCitando al tweet mostrado " + quote)
						self.addphotobutton()
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "111"
					self.tweettext = msg.text()
					self.quote = quote
			if self.attachments[0].type == "video":
				if quote == None:
					if msg.text().isspace() or msg.text() == "":
						self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con 1 vídeo adjunto")
						self.removeattachmentbutton()
						self.addquotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "050"
					else:
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + msg.text() + "\nCon 1 vídeo adjunto")
						self.tweettext = msg.text()
						self.removeattachmentbutton()
						self.addquotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "150"
				else:
					if msg.text().isspace() or msg.text() == "":
						self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con 1 vídeo citando al tweet mostrado " + quote)
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "051"
					else:
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + msg.text() + "\nCon 1 vídeo\nCitando al tweet mostrado " + quote)
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "151"
					self.tweettext = msg.text()
					self.quote = quote
			if self.attachments[0].type == "animated_gif":
				if quote == None:
					if msg.text().isspace() or msg.text() == "":
						self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con un gif adjunto")
						self.removeattachmentbutton()
						self.addquotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "060"
					else:
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + msg.text() + "\nCon 1 gif adjunto")
						self.tweettext = msg.text()
						self.removeattachmentbutton()
						self.addquotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "160"
				else:
					if msg.text().isspace() or msg.text() == "":
						self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con 1 gif citando al tweet mostrado " + quote)
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "061"
					else:
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + msg.text() + "\nCon 1 gif\nCitando al tweet mostrado " + quote)
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "161"
					self.tweettext = msg.text()
					self.quote = quote
		except api.NoAttachmentException:
			self.creationdate = datetime.datetime.now()
			try:
				quote = msg.url()
			except api.NoUrlException:
				quote = None
			if quote == None:
				self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + msg.text())
				self.tweettext = msg.text()
				self.addattachmentbutton()
				self.addquotebutton()
				self.addsendbutton()
				self.addcancelbutton()
				self.status = "100"
			else:
				if msg.text().isspace() or msg.text() == "":
					self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto citando al tweet mostrado " + quote)
					self.addattachmentbutton()
					self.removequotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "001"
				else:
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + msg.text() + "\nCitando al tweet mostrado " + quote)
					self.addattachmentbutton()
					self.removequotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "101"
				self.tweettext = msg.text()
				self.quote = quote
	
	def statusX14X(self, msg):
		try:
			attachment = api.attachment.frommsg(msg)
			if attachment.type == "photo" and len(self.attachments) == 4:
				responsetext = "ERROR: Sólo se pueden adjuntar un máximo de 4 fotos\n\n"
			elif attachment.type != "photo":
				responsetext = "ERROR: No se pueden adjuntar vídeos/gifs junto a fotos\n\n"
			else:
				self.attachments.append(attachment)
				responsetext = ""
			try:
				self.quote = msg.url()
			except api.NoUrlException:
				pass
			msgtext = msg.text()
			if self.quote == "":
				if msgtext.isspace() or msgtext == "":
					if self.tweettext == "" or self.tweettext.isspace():
						responsetext += "Se publicará un tweet sin texto con " + str(len(self.attachments)) + " fotos adjuntas"
						self.response = api.msg.create(self.user_id, responsetext)
						if len(self.attachments) == 4:
							self.removeattachmentbutton()
							self.addquotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						else:
							self.addphotobutton()
							self.removeattachmentbutton()
							self.addquotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						self.status = "0" + str(len(self.attachments)) + "0"
					else:
						responsetext += "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon " + str(len(self.attachments)) + " fotos adjuntas"
						self.response = api.msg.create(self.user_id, responsetext)
						if len(self.attachments) == 4:
							self.removeattachmentbutton()
							self.addquotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						else:
							self.addphotobutton()
							self.removeattachmentbutton()
							self.addquotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						self.status = "1" + str(len(self.attachments)) + "0"
				else:
					self.tweettext = msg.text()
					responsetext += "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon " + str(len(self.attachments)) + " fotos adjuntas"
					self.response = api.msg.create(self.user_id, responsetext)
					if len(self.attachments) == 4:
						self.removeattachmentbutton()
						self.addquotebutton()
						self.addsendbutton()
						self.addcancelbutton()
					else:
						self.addphotobutton()
						self.removeattachmentbutton()
						self.addquotebutton()
						self.addsendbutton()
						self.addcancelbutton()
					self.status = "1" + str(len(self.attachments)) + "0"
			else:
				if msgtext.isspace() or msgtext == "":
					if self.tweettext == "" or self.tweettext.isspace():
						responsetext += "Se publicará un tweet sin texto con " + str(len(self.attachments)) + " fotos\nCitando al tweet mostrado " + self.quote
						self.response = api.msg.create(self.user_id, responsetext)
						if len(self.attachments) == 4:
							self.removeattachmentbutton()
							self.removequotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						else:
							self.addphotobutton()
							self.removeattachmentbutton()
							self.removequotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						self.status = "0" + str(len(self.attachments)) + "1"
					else:
						responsetext += "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon " + str(len(self.attachments)) + " fotos adjuntas\nCitando al tweet mostrado " + self.quote 
						self.response = api.msg.create(self.user_id, responsetext)
						if len(self.attachments) == 4:
							self.removeattachmentbutton()
							self.addquotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						else:
							self.addphotobutton()
							self.removeattachmentbutton()
							self.removequotebutton()
							self.addsendbutton()
							self.addcancelbutton()
						self.status = "1" + str(len(self.attachments)) + "1"
				else:
					self.tweettext = msg.text()
					responsetext += "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon " + str(len(self.attachments)) + " fotos adjuntas\nCitando al tweet mostrado " + self.quote
					self.response = api.msg.create(self.user_id, responsetext)
					if len(self.attachments) == 4:
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
					else:
						self.addphotobutton()
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
					self.status = "1" + str(len(self.attachments)) + "1"

		except api.NoAttachmentException:
			try:
				self.quote = msg.url()
			except api.NoUrlException:
				pass
			msgtext = msg.text()
			if msgtext.isspace() or msgtext == "":
				if self.tweettext == "" or self.tweettext.isspace():
					self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con " + str(len(self.attachments)) + " fotos adjuntas\nCitando al tweet mostrado " + self.quote)
					if len(self.attachments) == 4:
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
					else:
						self.addphotobutton()
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
					self.status = "0" + str(len(self.attachments)) + "1"
				else:
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon " + str(len(self.attachments)) + " fotos adjuntas\nCitando al tweet mostrado " + self.quote)
					if len(self.attachments) == 4:
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
					else:
						self.addphotobutton()
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
					self.status = "1" + str(len(self.attachments)) + "1"
			else:
				self.tweettext = msg.text()
				if self.quote == "":
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon " + str(len(self.attachments)) + " fotos adjuntas")
					if len(self.attachments) == 4:
						self.removeattachmentbutton()
						self.addquotebutton()
						self.addsendbutton()
						self.addcancelbutton()
					else:
						self.addphotobutton()
						self.removeattachmentbutton()
						self.addquotebutton()
						self.addsendbutton()
						self.addcancelbutton()
					self.status = "1" + str(len(self.attachments)) + "0"
				else:
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon " + str(len(self.attachments)) + " fotos adjuntas\nCitando al tweet mostrado " + self.quote)
					if len(self.attachments) == 4:
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
					else:
						self.addphotobutton()
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
					self.status = "1" + str(len(self.attachments)) + "1"

	def statusX56X(self, msg):
		try:
			attachment = api.attachment.frommsg(msg)
			if self.response.text().split()[0] == "ERROR:":
				responsetext = self.response.text().split("\n\n")[1]
				self.response.chtext("ERROR: No se pueden adjuntar más elementos tras adjuntar un vídeo/gif\n\n" + responsetext)
			else:
				self.response.chtext("ERROR: No se pueden adjuntar más elementos tras adjuntar un vídeo/gif\n\n" + self.response.text())
		except api.NoAttachmentException:
			switcher = {
				"video": ("vídeo", "5"),
				"animated_gif": ("gif", "6")
			}
			try:
				self.quote = msg.url()
			except api.NoUrlException:
				pass
			if msg.text().isspace() or msg.text() == "":
				if self.tweettext == "" or self.tweettext.isspace():
					self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto con 1 " + switcher[self.attachments[0].type][0] + " adjunto citando al tweet mostrado " + self.quote)
					self.removeattachmentbutton()
					self.removequotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "0" + switcher[self.attachments[0].type][1] + "1"
				else:
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 " + switcher[self.attachments[0].type][0] + " adjunto\nCitando al tweet mostrado " + self.quote)
					self.removeattachmentbutton()
					self.removequotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "1" + switcher[self.attachments[0].type][1] + "1"
			else:
				self.tweettext = msg.text()
				if self.quote == "":
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 " + switcher[self.attachments[0].type][0] + " adjunto")
					self.removeattachmentbutton()
					self.addquotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "1" + switcher[self.attachments[0].type][1] + "0"
				else:
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 " + switcher[self.attachments[0].type][0] + " adjunto\nCitando el tweet mostrado " + self.quote)
					self.removeattachmentbutton()
					self.removequotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "1" + switcher[self.attachments[0].type][1] + "1"

	def statusX0X(self, msg):
		try:
			self.attachments.append(api.attachment.frommsg(msg))
			try:
				self.quote = msg.url()
			except api.NoUrlException:
				pass
			if self.attachments[0].type == "photo":
				if msg.text().isspace() or msg.text() == "":
					if self.tweettext == "":
						self.response = api.msg.create(self.user_id, "Se publicará un tweet con 1 foto citando al tweet mostrado " + self.quote)
						self.addphotobutton()
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "011"
					else:
						if self.quote == "":
							self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 foto adjunta")
							self.addphotobutton()
							self.removeattachmentbutton()
							self.addquotebutton()
							self.addsendbutton()
							self.addcancelbutton()
							self.status = "110"
						else:
							self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 foto adjunta\nCitando al tweet mostrado " + self.quote)
							self.addphotobutton()
							self.removeattachmentbutton()
							self.removequotebutton()
							self.addsendbutton()
							self.addcancelbutton()
							self.status = "111"
				else:
					self.tweettext = msg.text()
					if self.quote == "":
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 foto adjunta")
						self.addphotobutton()
						self.removeattachmentbutton()
						self.addquotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "110"
					else:
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 foto adjunta\nCitando al tweet mostrado: " + self.quote)
						self.addphotobutton()
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "111"
			elif self.attachments[0].type == "video":
				if msg.text().isspace() or msg.text() == "":
					if self.tweettext == "":
						self.response = api.msg.create(self.user_id, "Se publicará un tweet con 1 vídeo citando al tweet mostrado " + self.quote)
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "051"
					else:
						if self.quote == "":
							self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 vídeo adjunto")
							self.removeattachmentbutton()
							self.addquotebutton()
							self.addsendbutton()
							self.addcancelbutton()
							self.status = "150"
						else:
							self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 vídeo adjunto\nCitando al tweet mostrado " + self.quote)
							self.removeattachmentbutton()
							self.removequotebutton()
							self.addsendbutton()
							self.addcancelbutton()
							self.status = "151"
				else:
					self.tweettext = msg.text()
					if self.quote == "":
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 vídeo adjunto")
						self.removeattachmentbutton()
						self.addquotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "150"
					else:
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 vídeo adjunto\nCitando al tweet mostrado: " + self.quote)
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "151"
			elif self.attachments[0].type == "animated_gif":
				if msg.text().isspace() or msg.text() == "":
					if self.tweettext == "":
						self.response = api.msg.create(self.user_id, "Se publicará un tweet con 1 gif citando al tweet mostrado " + self.quote)
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "061"
					else:
						if self.quote == "":
							self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 gif adjunto")
							self.removeattachmentbutton()
							self.addquotebutton()
							self.addsendbutton()
							self.addcancelbutton()
							self.status = "160"
						else:
							self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 gif adjunto\nCitando al tweet mostrado " + self.quote)
							self.removeattachmentbutton()
							self.removequotebutton()
							self.addsendbutton()
							self.addcancelbutton()
							self.status = "161"
				else:
					self.tweettext = msg.text()
					if self.quote == "":
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 gif adjunto")
						self.removeattachmentbutton()
						self.addquotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "160"
					else:
						self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCon 1 gif adjunto\nCitando al tweet mostrado: " + self.quote)
						self.removeattachmentbutton()
						self.removequotebutton()
						self.addsendbutton()
						self.addcancelbutton()
						self.status = "161"

		except api.NoAttachmentException:
			try:
				self.quote = msg.url()
			except api.NoUrlException:
				pass
			if msg.text().isspace() or msg.text() == "":
				if self.tweettext == "":
					self.response = api.msg.create(self.user_id, "Se publicará un tweet sin texto citando al tweet mostrado " + self.quote)
					self.addattachmentbutton()
					self.removequotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "001"
				else:
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCitando al tweet mostrado " + self.quote)
					self.addattachmentbutton()
					self.removequotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "101"
			else:
				self.tweettext = msg.text()
				if self.quote == "":
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext)
					self.addattachmentbutton()
					self.addquotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "100"
				else:
					self.response = api.msg.create(self.user_id, "Se publicará el siguiente tweet:\n" + self.tweettext + "\nCitando al tweet mostrado " + self.quote)
					self.addattachmentbutton()
					self.removequotebutton()
					self.addsendbutton()
					self.addcancelbutton()
					self.status = "101"

	def tweetpost(self):
		tweet = api.tweet.create(self.tweettext)
		if self.quote != "":
			tweet.quote(self.quote)
		for attachment in self.attachments:
			tweet.attach(attachment)
		sleep(10)
		self.tweets.append((tweet.post(), datetime.datetime.now()))

	def read(self, msg):
		quickreply = msg.quickreplyresponse()
		if quickreply == None:
			if self.status[1] in ["1", "2", "3", "4"]:
				self.statusX14X(msg)
			elif self.status[1] in ["5", "6"]:
				self.statusX56X(msg)
			elif self.status[1] == "0" and self.status != "000":
				self.statusX0X(msg)
			else:
				self.status000(msg)
		else:
			if quickreply == "Adjuntar una foto, vídeo o gif": 
				self.addattachment(msg)
			elif quickreply == "Adjuntar una foto":
				self.addphoto(msg)
			elif quickreply == "Enviar tweet":
				self.send()
			elif quickreply == "Citar tweet":
				self.addquote()
			elif quickreply == "Cancelar":
				self.cancel()
			elif quickreply == "Eliminar último archivo adjunto":
				self.removeattachment()
			elif quickreply == "Eliminar tweet citado":
				self.removequote()
		self.response.post()
		if self.pendingnot != []:
			for noti in self.pendingnot:
				noti.post()

	def notify(self, text, link, replylink=None):
		noti = api.msg.create(self.user_id, text)
		notilink = api.msg.create(self.user_id, link)
		if self.status == "000":
			notilink.post()
			noti.post()
		else:
			self.pendingnot.append(notilink)
			self.pendingnot.append(noti)
