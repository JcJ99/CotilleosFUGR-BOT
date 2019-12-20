from django.http import HttpResponse
from .challenge_handler import challenge

def webhook(request):
    if request.method == "GET":
        try:
            challenge(request.GET.get("crc_token"))
            return HttpResponse("OK")
        except TypeError:
            return HttpResponse("Si no eres Twitter no me interesas")
    elif request.method == "POST":
        pass