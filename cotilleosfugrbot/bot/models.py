from django.db import models
import datetime

class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    punishment = models.CharField(max_length=6, default=None)
    punishment_end = models.DateTimeField(default=None)

    def __str__(self):
        return "<Conversation Id: %i>" % id

class Tweet(models.Model):
    id = models.BigIntegerField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "<Tweet id: %i>" % id