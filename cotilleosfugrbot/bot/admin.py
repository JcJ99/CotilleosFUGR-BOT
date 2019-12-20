from django.contrib import admin
from .models import User, Tweet

admin.site.register(User)
admin.site.register(Tweet)