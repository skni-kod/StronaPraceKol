from django import forms
from django.contrib import admin, messages
from django.core.mail import EmailMultiAlternatives, BadHeaderError
from django.urls import path
from django.views.generic import FormView
from django_summernote.admin import SummernoteModelAdmin
from django_summernote.fields import SummernoteTextFormField

from StronaProjektyKol.settings import SITE_ADMIN_MAIL
from .models import *


class AnnouncementAdmin(SummernoteModelAdmin):
    summernote_fields = '__all__'


class MassEmailModel(models.Model):
    class Meta:
        verbose_name_plural = 'Mass email'
        app_label = 'papers'


class MassEmailForm(forms.Form):
    RECIPIENT_CHOICES = (
        ('1', 'Do wszystkich'),
        ('2', 'Artykuł zgłoszony jako gotowy'),
        ('3', 'Artykuł uznany jako "Przyjęty"')
    )

    subject = forms.CharField(label='Temat')
    recipients = forms.ChoiceField(label='Adresaci', choices=RECIPIENT_CHOICES)
    content = SummernoteTextFormField(label='Treść')


class MassEmailView(FormView):
    template_name = 'papers/mass_email.html'
    form_class = MassEmailForm
    success_url = '/admin'

    def form_valid(self, form):
        if form.is_valid():
            recipients_choice = form.cleaned_data['recipients']

            recipients = []
            users = User.objects.all()
            # ALL USERS
            if recipients_choice == '1':
                recipients = users
            # HAS PAPER WITH FLAG APPROVED
            elif recipients_choice == '2':
                for user in users:
                    for paper in user.paper_set.all():
                        if paper.approved:
                            recipients.append(user)
                            break
            # HAS PAPER WITH REVIEW THAT HAS FINAL GRADE == APPROVE
            elif recipients_choice == '3':
                for user in users:
                    for paper in user.paper_set.all():
                        for review in paper.review_set.all():
                            if int(review.final_grade.value) == 1:
                                recipients.append(user)
                                break
            emails = []
            for recipient in recipients:
                emails.append(recipient.email)
            # Send message
            for email in emails:
                try:
                    msg = EmailMultiAlternatives(form.cleaned_data['subject'], form.cleaned_data['content'],
                                                 SITE_ADMIN_MAIL, list(email), headers={'Reply-To': SITE_ADMIN_MAIL})
                    msg.attach_alternative(form.cleaned_data['content'], "text/html")
                    msg.send()
                    bad = 0
                except BadHeaderError:
                    messages.add_message(self.request, messages.WARNING, 'Unable to send mail')
                    bad = 1
            if not bad:
                messages.add_message(self.request, messages.SUCCESS, f'Message sent to {len(emails)} users')
        return super().form_valid(form)


class MassEmailModelAdmin(admin.ModelAdmin):
    model = MassEmailModel

    def get_urls(self):
        mass_email = '{}_{}_changelist'.format(
            self.model._meta.app_label, self.model._meta.model_name)
        return [
            path('mass_email/', self.admin_site.admin_view(MassEmailView.as_view()), name=mass_email),
        ]


admin.site.register(StudentClub)
admin.site.register(Grade)
admin.site.register(Paper)
admin.site.register(CoAuthor)
admin.site.register(UploadedFile)
admin.site.register(Review)
admin.site.register(Message)
admin.site.register(MessageSeen)
admin.site.register(NotificationPeriod)
admin.site.register(MassEmailModel, MassEmailModelAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
