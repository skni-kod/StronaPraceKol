from django.contrib import admin
from .models import StudentClub, Paper, Review, UploadedFile, Message, Announcement

admin.site.register(StudentClub)
admin.site.register(Paper)
admin.site.register(Review)
admin.site.register(UploadedFile)
admin.site.register(Message)
admin.site.register(Announcement)
