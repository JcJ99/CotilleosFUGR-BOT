import requests
import base64
import os
import json
import readline
import datetime
import sys
import pip
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, DateTime, BigInteger, String, case, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

url = ""
bearer_auth = None
database_url = ""
base_engine = None
Base = declarative_base()
Session = None
session = None

class Conversation_model(Base):
	__tablename__ = "conversations"
	id = Column(BigInteger, primary_key=True)
	tweets = relationship("Tweet_model", backref="conversation", cascade="all,delete")
	creation_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
	punishment_type = Column(String(7), default=None)
	punishment_end = Column(DateTime, default=None)
	admin = Column(Boolean, default=False)

	def __repr__(self):
		return "<Conversation: %r>" % self.id

class Tweet_model(Base):
	__tablename__ = "tweets"
	id = Column(BigInteger, primary_key=True)
	creation_date = Column(DateTime, nullable=False)
	conversation_id = Column(BigInteger, ForeignKey("conversations.id"), nullable=False)

	def __repr__(self):
		return "<Tweet: %r>" % self.id

class InputException(BaseException):
	def __init__(self, message):
		self.sterr = message

class bearer_auth_handler(requests.auth.AuthBase):
	def __init__(self, bearer_key):
		self.bearer_key = bearer_key

	def __call__(self, r):
		r.headers["Authorization"] = "Bearer " + self.bearer_key
		return r

def ask_url():
	global url, bearer_auth, database_url, base_engine, Session, session
	url = input("Introduzca la url del bot: ")
	psw = input("Introduzca Contraseña de administrador: ")
	while True:
		if len(url) != 0 and url[len(url)-1] == "/":
			url = url[:len(url)-1]
		try:
			r = requests.get(url + "/admin", headers={"password": psw})
			r.raise_for_status()
			bearer_auth = bearer_auth_handler(r.json()["bearer_token"])
			database_url = r.json()["database_url"]
			with open(".boturl", "w") as f:
				f.write(url)
			engine = create_engine(database_url, echo=False)
			Session = sessionmaker(bind=engine)
			session = Session()
			break
		except requests.exceptions.MissingSchema:
			url = input("Url no válida, vuelva a introducirla: ")
		except requests.exceptions.InvalidURL:
			url = input("Url no válida, vuelva a introducirla: ")
		except json.decoder.JSONDecodeError:
			url = input("La url no corresponde con ningún bot, vuelva a introducirla: ")
		except KeyError:
			url = input("La url no corresponde con ningún bot, vuelva a introducirla: ")
		except requests.exceptions.HTTPError as e:
			if e.response.status_code == 404:
				url = input("La url no existe, vuelva a introducirla: ")
			elif e.response.status_code == 400:
				psw = input("Contraseña no válida vuelva a introducirla: ")
			else:
				raise

#Function for obtaining user id from screen name
def getuserid(*screen_names):
	par = {"screen_name": screen_names}
	r = requests.get("https://api.twitter.com/1.1/users/lookup.json", auth=bearer_auth, params=par)
	r.raise_for_status()
	return [user["id_str"] for user in r.json()]

#Function for obtaining user_name from id
def getusername(*ids):
	par = {"user_id": ids}
	r = requests.get("https://api.twitter.com/1.1/users/lookup.json", auth=bearer_auth, params=par)
	r.raise_for_status()
	return [user["screen_name"] for user in r.json()]

def list_command(*args):
	when = {
		"ban": 2,
		"timeout": 1,
		None: 0
	}
	sort = case(value=Conversation_model.punishment_type, whens=when)
	convs = session.query(Conversation_model).order_by(sort).all()
	if convs:
		users_name = getusername(*tuple([conv.id for conv in convs]))
		for i,conv in enumerate(convs):
			if conv.punishment_type == "timeout":
				punishment_end = conv.punishment_end.strftime("%H:%M:%S %d/%m/%Y")
			else:
				punishment_end = None
			output = "@{0: <20} id: {1: <20} admin: {2}\tcastigo: {3: <7} hasta: {4}".format(users_name[i], conv.id, conv.admin ,str(conv.punishment_type), str(punishment_end))
			print(output)
	else:
		print("Ningún usuario en el registro")

def exit_command(*args):
	raise KeyboardInterrupt

def timeout_command(*args):
	try:
		user = args[0]
		days = args[1]
		days = int(days)
		user_id = getuserid(user)[0]
	except IndexError:
		raise InputException("Uso: timeout <usuario (@)> <dias (Nº Entero)>")
	except ValueError:
		raise InputException("Uso: timeout <usuario (@)> <dias (Nº Entero)>")
	except requests.exceptions.HTTPError as e:
		if e.response.status_code == 404:
			raise InputException("El usuario no existe")

	user = session.query(Conversation_model).get(user_id)
	if user:
		user.punishment_type = "timeout"
		user.punishment_end = datetime.datetime.utcnow() + datetime.timedelta(days=days)
		session.commit()
	else:
		user = Conversation_model(id=user_id, punishment_type="timeout", punishment_end=datetime.datetime.utcnow() + datetime.timedelta(days=days))
		session.add(user)
		session.commit()

def ban_command(*args):
	try:
		user = args[0]
		user_id = getuserid(user)[0]
	except IndexError:
		raise InputException("Uso: ban <usuario (@)>")
	except ValueError:
		raise InputException("Uso: ban <usuario (@)>")
	except requests.exceptions.HTTPError as e:
		if e.response.status_code == 404:
			raise InputException("El usuario no existe")

	user = session.query(Conversation_model).get(user_id)
	if user:
		user.punishment_type = "ban"
		session.commit()
	else:
		user = Conversation_model(id=user_id, punishment_type="ban")
		session.add(user)
		session.commit()

def forgive_command(*args):
	try:
		user = args[0]
		user_id = getuserid(user)[0]
	except IndexError:
		raise InputException("Uso: forgive <usuario (@)>")
	except requests.exceptions.HTTPError as e:
		if e.response.status_code == 404:
			raise InputException("El usuario no existe")

	user = session.query(Conversation_model).get(user_id)
	if user.punishment_type != None:
		user.punishment_type = None
		user.punishment_end = None
		session.commit()
	else:
		raise InputException("El usuario @{0} no está castigado".format(user))

def identify_command(*args):
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
			raise InputException("Uso: identify <id/link del tweet>")
	except IndexError:
		raise InputException("Uso: identify <id/link del tweet>")
	
	tweet = session.query(Tweet_model).get(tweet_id)
	if tweet:
		user_id = tweet.conversation.id
		print("El tweet fue publicado por @{0}".format(getusername(user_id)[0]))
	else:
		print("El tweet no fue publicado por un usuario registrado")

def deleteuser_command(*args):
	try:
		user = args[0]
		user_id = getuserid(user)[0]
	except IndexError:
		raise InputException("Uso: deleteuser <usuario (@)>")
	except requests.exceptions.HTTPError as e:
		if e.response.status_code == 404:
			raise InputException("El usuario no existe")

	user_mod = session.query(Conversation_model).get(user_id)
	if user_mod:
		session.delete(user_mod)
		session.commit()
	else:
		raise InputException("El usuario @{0} no está registrado".format(user))

def admin_command(*args):
	try:
		user = args[0]
		user_id = getuserid(user)[0]
	except IndexError:
		raise InputException("Uso: admin <usuario (@)>")
	except ValueError:
		raise InputException("Uso: admin <usuario (@)>")
	except requests.exceptions.HTTPError as e:
		if e.response.status_code == 404:
			raise InputException("El usuario no existe")

	user = session.query(Conversation_model).get(user_id)
	if user:
		if user.admin:
			user.admin = False
		else:
			user.admin = True
		session.commit()
	else:
		user = Conversation_model(id=user_id, admin=True)
		session.add(user)
		session.commit()

commands = {
	"list": (list_command, "Muestra los usuarios reconocidos por el bot"),
	"timeout": (timeout_command, "Evita que un usuario twitee por un tiempo"),
	"ban": (ban_command, "Evita que un usuario twitee para siempre"),
	"forgive": (forgive_command, "Elimina el castigo de un usuario"),
	"identify": (identify_command, "Revela el autor de un tweet publicado"),
	"deleteuser": (deleteuser_command, "Elimina un usuario de la base de datos"),
	"admin": (admin_command, "Otorga o revoca permisos de administrador a un usuario"),
	"exit": (exit_command, "Desconexión")
}

def main():
	global url, bearer_auth, database_url, base_engine, Session, session
	file = False
	print("CLIENTE COTILLEOS FÍSICA UGR")
	try:
		if os.path.isfile(".boturl"):
			with open(".boturl", "r") as f:
				url = f.read()
				file = True
			print("Se conectará a la url: " + url)
			change = input("¿Desea cambiar la url? (s/n): ")
			if change in ["si", "sí", "s", "y", "yes"]:
				ask_url()
			else:
				firsttry = True
				while True:
					try:
						if firsttry:
							psw = input("Introduzca Contraseña de administrador: ")
						else:
							psw = input("Contraseña no válida vuelva a introducirla: ")
						r = requests.get(url + "/admin", headers={"password": psw})
						r.raise_for_status()
						bearer_auth = bearer_auth_handler(r.json()["bearer_token"])
						database_url = r.json()["database_url"]
						with open(".boturl", "w") as f:
							f.write(url)
						engine = create_engine(database_url, echo=False)
						Session = sessionmaker(bind=engine)
						session = Session()
						break
					except json.decoder.JSONDecodeError:
						url = input("La url no corresponde con ningún bot, vuelva a introducirla: ")
					except KeyError:
						url = input("La url no corresponde con ningún bot, vuelva a introducirla: ")
					except requests.exceptions.HTTPError as e:
						if e.response.status_code == 404:
							url = input("La url no existe, vuelva a introducirla: ")
						elif e.response.status_code == 400:
							firsttry = False
						else:
							raise
		else:
			ask_url()

		print("Conectado correctamente")

		while True:
			try:
				inpt = input("cotilleosfugrbot~$ ")
				inpt = inpt.split()
				try:
					commands[inpt[0]][0](*tuple(inpt[1::]))
				except KeyError:
					print("Comandos disponibles:")
					for command, value in commands.items():
						print("   {0: <12}{1}".format(command, value[1]))
				except IndexError:
					pass
				except InputException as e:
					print(e.sterr)
			except requests.exceptions.HTTPError:
				raise
				print("Se ha perdido la conexión con el bot, vuelva a conectar")
				ask_url()

	except KeyboardInterrupt:
		print("")

if __name__ == "__main__":
	main()