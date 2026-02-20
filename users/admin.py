from .models import UserDetail, ContactInfo, Announcement
from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin


class AnnouncementAdmin(SummernoteModelAdmin):
    summernote_fields = '__all__'


admin.site.register(UserDetail)
admin.site.register(ContactInfo)
admin.site.register(Announcement, AnnouncementAdmin)
