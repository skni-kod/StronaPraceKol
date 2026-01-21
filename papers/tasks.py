from django_q.tasks import schedule
from django_q.models import Schedule


def setup_scheduled_tasks():
    func = 'papers.notifications.send_statement_reminder'
    qs = Schedule.objects.filter(func=func).order_by('id')

    if qs.count() > 1:
        keep = qs.first()
        qs.exclude(id=keep.id).delete()
        schedule_obj = keep
    elif qs.exists():
        schedule_obj = qs.first()
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
    else:
        Schedule.objects.create(**defaults)
