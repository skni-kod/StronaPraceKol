from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from StronaProjektyKol.settings import SITE_ADMIN_MAIL

def send_message_notification_email(message):
    paper = message.paper
    author = paper.author
    sender = message.author

    if sender == author:
        return

    if not author.email:
        return

    subject = f'Nowa wiadomość dotycząca Twojego artykułu: {paper.title}'

    context = {
        'author_name': f'{author.first_name} {author.last_name}',
        'sender_name': f'{sender.first_name} {sender.last_name}',
        'paper_title': paper.title,
        'message_text': message.text,
        'message_date': message.created_at,
        'reviewer_name': f'{message.reviewer.first_name} {message.reviewer.last_name}' if message.reviewer else 'System',
    }

    html_message = render_to_string('email/message_notification.html', context)
    plain_message = render_to_string('email/message_notification.txt', context)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=SITE_ADMIN_MAIL,
        recipient_list=[author.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_paper_creation_notification_email(paper):
    author = paper.author

    if not author.email:
        return

    subject = f'Potwierdzenie utworzenia artykułu: {paper.title}'
    context = {
        'paper': paper,
    }

    html_message = render_to_string('email/paper_creation_notification.html', context)
    plain_message = render_to_string('email/paper_creation_notification.txt', context)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=SITE_ADMIN_MAIL,
        recipient_list=[author.email],
        html_message=html_message,
        fail_silently=False,
    )