from django.contrib import admin
from .models import StudentClub, Paper, CoAuthor, UploadedFile, Review, Message, MessageSeen, Announcement


admin.site.register(StudentClub)
admin.site.register(Paper)
admin.site.register(CoAuthor)
admin.site.register(UploadedFile)
admin.site.register(Review)
admin.site.register(Message)
admin.site.register(MessageSeen)
admin.site.register(Announcement)
