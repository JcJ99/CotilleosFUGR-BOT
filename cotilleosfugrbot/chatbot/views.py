from django.http import HttpResponse, JsonResponse
import logging
import hmac
import hashlib
import base64
import json
from .Auths import consumer_secret
from .chatbot import associate, cleanconvers

logger = logging.getLogger(__name__)

def hello_world(request):
    return HttpResponse("Aquí sigo mona")

def webhook(request):
    if request.method == "GET":
        crc_token = request.GET.get("crc_token", "")
        b = bytearray()
        b.extend(map(ord, crc_token))
        b2 = bytearray()
        b2.extend(map(ord, consumer_secret))
        sha256_hash_digest = hmac.new(b2, msg=b, digestmod=hashlib.sha256).digest()
        response = {
            'response_token': 'sha256=' + "".join(map(chr, base64.b64encode(sha256_hash_digest)))
        }
        return JsonResponse(response)
    elif request.method == "POST":
        data = json.loads(request.body)
        associate(data)
        cleanconvers()
        return HttpResponse("OK")
