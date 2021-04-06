from django.contrib import admin

from .models import Message, MessageSeen

admin.site.register(Message)
admin.site.register(MessageSeen)
