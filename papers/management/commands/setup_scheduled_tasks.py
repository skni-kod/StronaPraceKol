from django.core.management.base import BaseCommand
from django_q.models import Schedule


class Command(BaseCommand):
    help = 'Setup scheduled tasks for django-q'

    def handle(self, *args, **options):
        func = 'papers.notifications.send_statement_reminder'
        qs = Schedule.objects.filter(func=func).order_by('id')

        if qs.count() > 1:
            keep = qs.first()
            qs.exclude(id=keep.id).delete()
            schedule_obj = keep
            self.stdout.write(self.style.WARNING(f'Usunięto duplikaty, zachowano: {keep.id}'))
        elif qs.exists():
            schedule_obj = qs.first()
            self.stdout.write(self.style.SUCCESS('Harmonogram już istnieje'))
        else:
            schedule_obj = None

        defaults = {
            'name': 'daily_statement_reminder',
            'schedule_type': Schedule.DAILY,
            'repeats': -1,
            'func': func,
        }

        if schedule_obj:
            schedule_obj.name = defaults['name']
            schedule_obj.schedule_type = defaults['schedule_type']
            schedule_obj.repeats = defaults['repeats']
            schedule_obj.save()
            self.stdout.write(self.style.SUCCESS('Harmonogram zaktualizowany'))
        else:
            Schedule.objects.create(**defaults)
            self.stdout.write(self.style.SUCCESS('Harmonogram utworzony'))
