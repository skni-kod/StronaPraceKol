from django.contrib import admin
from django.urls import path, reverse_lazy
from django.views.generic import FormView
from django.core.mail import EmailMultiAlternatives
from .models import *
from django import forms


admin.site.register(StudentClub)
admin.site.register(Grade)
admin.site.register(Paper)
admin.site.register(CoAuthor)
admin.site.register(UploadedFile)
admin.site.register(Review)
admin.site.register(Announcement)
admin.site.register(Message)
admin.site.register(MessageSeen)
admin.site.register(NotificationPeriod)


# my dummy model
class DummyModel(models.Model):
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
    content = forms.CharField(widget=forms.Textarea, label='Treść')


class MassEmailView(FormView):
    template_name = 'papers/mass_email.html'
    form_class = MassEmailForm
    success_url = '/admin'

    def form_valid(self, form):
        if form.is_valid():
            recipients_choice = form.cleaned_data['recipients']
            if recipients_choice == 1:
                recipients = User.objects.all()
            elif recipients_choice == 2:
                pass
            elif recipients_choice == 3:
                pass
        return super().form_valid(form)


class DummyModelAdmin(admin.ModelAdmin):
    model = DummyModel

    def get_urls(self):
        mass_email = '{}_{}_changelist'.format(
            self.model._meta.app_label, self.model._meta.model_name)
        return [
            path('mass_email/', self.admin_site.admin_view(MassEmailView.as_view()), name=mass_email),
        ]


admin.site.register(DummyModel, DummyModelAdmin)
