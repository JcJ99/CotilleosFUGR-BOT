from cotilleosfugrbot import *
from api_handler import *
from conver_handler import *
import json
from time import sleep

with open("msg.json") as f: 
	data = json.load(f)                                                                         

with open("msg2.json") as f: 
	data2 = json.load(f)

with open("msg3.json") as f:
	data3 = json.load(f)

associate(data)
associate(data2)
associate(data3)