import . import models
import .api_handler as api

class ConverError(BaseException):
	def __init__(self, string, critical=False):
		self.strerr = string
		self.critical = critical

"""Associates any twitter webhook request with its corresponding
   twitter interaction"""
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

#React to any twitter's request
def receive(request):
    #Switcher o possible requests
    switcher = {
        "dm":
    }

#React to a direct message
def msg_react(request):
	try:
		msg = api.msg(jsondata["direct_message_events"][0])
		user = User.query.get(msg.sid())
		if not user:
			user = User(id=msg.sid())
			user.save()
		if not msg.quickreplyresponse():
			#Text
			if not (msg.text() == "" or msg.text().isspace()):
				text = msg.text()
			#Quote
			try:
				quote = msg.url()
			except api.NoUrlException:
				quote = None
			#Attachment
			try:
				attachment = api.attachment.frommsg(msg)
			except api.NoAttachmentException:
				attachment = None
			current_tweet = user.pending_tweet_set.order_by("-date")[0]
			if not current_tweet:
				current_tweet = Pending_tweet(author=user, text=text, quote=quote)
			else:
				current_tweet.text = text
				if quote:
					current_tweet.quote = quote
	except ConverError:
		
# Sends a message as a response to a received tweet
def respond

# Quick replies
def sendtweetbutton(msg):
	msg.addquickreply("Publicar tweet",
	description="¡Publica tu tweet!",
	metadata="Enviar tweet")

def sendthreadbutton(msg):
	msg.addquickreply("Publicar hilo",
	description="¡Publica tu hilo!",
	metadata="Enviar tweet")

def cancelbutton(msg):
	msg.addquickreply("Cancelar",
	description="Borrar el tweet o el hilo",
	metadata="Cancelar")

def removeattachmentbutton(msg):
	msg.addquickreply("Eliminar último archivo adjunto",
	description="No se adjuntará en el tweet",
	metadata="Eliminar último archivo adjunto")

def removequotebutton(msg):
	msg.addquickreply("Eliminar tweet citado",
	description="No se citará en el tweet final",
	metadata="Eliminar tweet citado")

def addtweetbutton(msg):
	msg.addquickreply("Añadir tweet al hilo",
	description="Crea un nuevo tweet para formar un hilo",
	metadata="Añadir tweet al hilo")

def removetweetbutton(msg):
	msg.addquickreply("Eliminar último tweet del hilo",
	description="Elimina el tweet que estás editando",
	metadata="Eliminar último tweet del hilo")
