import hmac, base64, json, hashlib
from cotilleosfugrbot.settings import consumer_secret

def challenge(crc_token):
	b = bytearray()
	b.extend(map(ord, crc_token))
	b2 = bytearray()
	b2.extend(map(ord, consumer_secret))
	sha256_hash_digest = hmac.new(b2, msg=b, digestmod=hashlib.sha256).digest()
	response = {
		'response_token': 'sha256=' + "".join(map(chr, base64.b64encode(sha256_hash_digest)))
	}
	return json.dumps(response)