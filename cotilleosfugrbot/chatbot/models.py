from django.db import models

class User(models.Model):
    #BAN = "BAN"
    #TIMEOUT = "TMO"
    #NONE = "NAN"
    id = models.BigIntegerField(primary_key=True, editable=False)
    punishment_type = models.CharField(max_length=3, default="NAN", null=False)
    punishment_end = models.DateTimeField(null=True)
    is_admin = models.BooleanField(default=False)
    creationdate = models.DateTimeField(auto_now=True)

class Tweet(models.Model):
    id = models.BigIntegerField(primary_key=True, editable=False)
    text = models.CharField(max_length=240, null=False, editable=False)
    date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE)