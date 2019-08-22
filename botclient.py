import requests
from urllib.parse import quote_plus
import base64
import os
import json

data = []
url = ""
bearer_token = ""

class InputException(BaseException):
	def __init__(self, message):
		self.sterr = message

class bearer_auth(requests.auth.AuthBase):
	def __init__(self, bearer_key):
		self.bearer_key = bearer_key

	def __call__(self, r):
		r.headers["Authorization"] = "Bearer " + self.bearer_key
		return r

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
	r.raise_for_status()
	return r.json()["access_token"]

def ask_url():
	global url, bearer_token
	url = input("Introduce la url del bot: ")
	while True:
		if len(url) != 0 and url[len(url)-1] == "/":
			url = url[:len(url)-1]
		try:
			r = requests.get(url + "/admin")
		except requests.exceptions.MissingSchema:
			url = input("Url no válida, vuelva a introducirla: ")
			continue
		except requests.exceptions.InvalidURL:
			url = input("Url no válida, vuelva a introducirla: ")
			continue
		if r.status_code != 404:
			try:
				consumer = r.json()["credentials"]["consumer"]
				consumer_secret = r.json()["credentials"]["consumer_secret"]
				bearer_token = getbearertoken(consumer, consumer_secret)
				with open(".boturl", "w") as f:
					f.write(url)
				break
			except json.decoder.JSONDecodeError:
				url = input("La url no corresponde con ningún bot, vuelva a introducirla: ")
			except KeyError:
				url = input("La url no corresponde con ningún bot, vuelva a introducirla: ")
#Function for obtaining user id from screen name
def getuserid(*screen_names):
	par = {"screen_name": screen_names}
	auth = data
	r = requests.get("https://api.twitter.com/1.1/users/lookup.json", auth=bearer_auth(bearer_token), params=par)
	r.raise_for_status()
	return [user["id_str"] for user in r.json()]

#Function for obtaining user_name from id
def getusername(*ids):
	par = {"user_id": ids}
	r = requests.get("https://api.twitter.com/1.1/users/lookup.json", auth=bearer_auth(bearer_token), params=par)
	r.raise_for_status()
	return [user["screen_name"] for user in r.json()]

def list_command(*args):
	users = [conv for conv in data["conversations"]]
	users_id = [user["user_id"] for user in users]
	#Timeouted users second
	for i,user in enumerate(users):
		if user["punishment_type"] == "timeout":
			del users[i]
			del users_id[i]
			users.insert(0, user)
			users_id.insert(0, user["user_id"])
	#Banned users first
	for i,user in enumerate(users):
		if user["punishment_type"] == "ban":
			del users[i]
			del users_id[i]
			users.insert(0, user)
			users_id.insert(0, user["user_id"])
	if users != []:
		users_name = getusername(users_id)
		for i, (uid, name) in enumerate(zip(users_id, users_name)):
			print("@" + name + "\t" + "id: " + uid + "\t" + "castigo: " + str(users[i]["punishment_type"]) + "\t" + "hasta: " + str(users[i]["punishment_end"]))
	else:
		print("No hay usuarios reconocidos")

def exit_command(*args):
	raise KeyboardInterrupt

def timeout_command(*args):
	try:
		user = args[0][0]
		days = args[0][1]
		days = int(days)
	except IndexError:
		raise InputException("Uso: timeout <usuario (@)> <dias (Nº Entero)>")
	except ValueError:
		raise InputException("Uso: timeout <usuario (@)> <dias (Nº Entero)>")

	headers = {
		"user": user,
		"command": "timeout"
	}

	params = {
		"days": days
	}

	r = requests.post(url + "/admin", headers=headers, params=params)
	try:
		r.raise_for_status()
	except requests.HTTPError as e:
		if e.response.status_code == 400:
		 	raise InputException(e.response.text)
		else:
			raise

def ban_command(*args):
	try:
		user = args[0][0]
	except IndexError:
		raise InputException("Uso: ban <usuario>")

	headers = {
		"user": user,
		"command": "ban"
	}

	r = requests.post(url + "/admin", headers=headers)
	try:
		r.raise_for_status()
	except requests.HTTPError as e:
		if e.response.status_code == 400:
		 	raise InputException(e.response.text)
		else:
			raise

def forgive_command(*args):
	try:
		user = args[0][0]
	except IndexError:
		raise InputException("Uso: forgive <usuario>")

	headers = {
		"user": user,
		"command": "forgive"
	}

	r = requests.post(url + "/admin", headers=headers)
	try:
		r.raise_for_status()
	except requests.HTTPError as e:
		if e.response.status_code == 400:
		 	raise InputException(e.response.text)
		else:
			raise


commands = {
	"list": (list_command, "Muestra los usuarios reconocidos por el bot"),
	"timeout": (timeout_command, "Evita que un usuario twitee por un tiempo"),
	"ban": (ban_command, "Evita que un usuario twitee para siempre"),
	"forgive": (forgive_command, "Elimina el castigo de un usuario"),
	"exit": (exit_command, "Desconexión")
}

def main():
	global data, url, bearer_token
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
				r = requests.get(url + "/admin")
				consumer = r.json()["credentials"]["consumer"]
				consumer_secret = r.json()["credentials"]["consumer_secret"]
				bearer_token = getbearertoken(consumer, consumer_secret)
		else:
			ask_url()

		print("Conectado correctamente")

		while True:
			try:
				inpt = input("cotilleosfugrbot~$ ")
				inpt = inpt.split()
				if inpt[0] != "exit":
					r = requests.get(url + "/admin")
					r.raise_for_status()
					data = r.json()
				try:
					commands[inpt[0]][0](inpt[1::])
				except KeyError:
					print("Comandos disponibles:")
					for command, value in commands.items():
						print(command + "\t" + value[1])
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