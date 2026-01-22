from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from datetime import timedelta
from django.db.models import Q

from StronaProjektyKol.settings import SITE_ADMIN_MAIL, SITE_NAME, SITE_DOMAIN
from .models import Paper, NotificationPeriod


def send_statement_reminder():
    """
    Wysyła przypomnienia tylko dla artykułów bez oświadczenia i jeśli
    minęło wystarczająco dużo czasu od ostatniego przypomnienia.
    Domyślny okres to 24h, jeśli brak wpisu w NotificationPeriod.
    Zwraca liczbę wysłanych przypomnień.
    """
    notification_period = NotificationPeriod.objects.filter(name='statement_reminder').first()
    if notification_period and getattr(notification_period, 'period', None):
        period_delta = timedelta(seconds=notification_period.period)
    else:
        period_delta = timedelta(hours=24)

    now = timezone.now()
    threshold = now - period_delta

    papers_without_statement = Paper.objects.filter(
        (Q(statement=0) | Q(statement__isnull=True)),
    ).filter(
        Q(statement_reminder_sent__isnull=True) | Q(statement_reminder_sent__lt=threshold)
    )

    sent_count = 0

    for paper in papers_without_statement:
        emails = []
        if hasattr(paper, 'author') and paper.author and getattr(paper.author, 'email', None):
            emails = [paper.author.email]
        elif hasattr(paper, 'authors'):
            emails = [u.email for u in paper.authors.all() if u.email]

        if not emails:
            continue

        subject = f"Prośba o przesłanie oświadczenia — {paper.title}"
        html_body = render_to_string('emails/statement_reminder.html', {
            'paper': paper,
            'site_name': SITE_NAME,
            'site_domain': SITE_DOMAIN,
        })
        text_body = strip_tags(html_body)

        msg = EmailMultiAlternatives(subject, text_body, SITE_ADMIN_MAIL, emails)
        msg.attach_alternative(html_body, "text/html")
        try:
            msg.send()
            sent_count += 1
            paper.statement_reminder_sent = now
            paper.save(update_fields=['statement_reminder_sent'])
        except Exception:
            continue

    return sent_count
