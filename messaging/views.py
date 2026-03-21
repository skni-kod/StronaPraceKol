from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .utils import send_message_notification_email

from papers.models import Message, MessageSeen, Paper


@csrf_exempt
def render_message(request):
    return render(request, 'messaging/message.html', {
        'type': request.POST['type'],
    })


@csrf_exempt
def get_message(request):
    user = request.user
    paper = Paper.objects.filter(pk=request.POST['paper_id']).first()
    reviewer = get_selected_reviewer(request, paper)
    editor = get_selected_editor(request, paper)
    reviewer, editor = normalize_message_participants(request, paper, reviewer, editor)
    reviewer, editor = resolve_message_participants(user, paper, reviewer, editor)

    if has_user_access_to_messages(user, paper, reviewer, editor):
        last_message_id = int(request.POST['last_message_id'])

        messages = Message.objects.filter(paper=paper, pk__gt=last_message_id)
        if reviewer is not None:
            messages = messages.filter(reviewer=reviewer, editor__isnull=True)
        else:
            messages = messages.filter(editor=editor, reviewer__isnull=True)

        messages = messages.order_by('created_at')


        data = dict()
        for message in messages:
            tmp = {'author': f'{message.author.username}',
                   'author_name': f'{message.author.first_name} {message.author.last_name}',
                   'date': f'{message.created_at.strftime("%d %b %H:%M")}', 'text': f'{message.text}',
                 'id': f'{message.pk}'}
            data[message.pk] = tmp

            # add seen record
            if message.author == user:
                continue

            if MessageSeen.objects.filter(message=message, reader=user).first() is None:
                MessageSeen.objects.create(
                    message=message,
                    reader=request.user,
                )

        return JsonResponse(data)
    else:
        response = HttpResponse()
        response.status_code = 401
        return response


@csrf_exempt
def send_message(request):
    response = HttpResponse()

    if request.method == "POST":
        user = request.user
        paper = Paper.objects.filter(pk=request.POST['paper_id']).first()
        reviewer = get_selected_reviewer(request, paper)
        editor = get_selected_editor(request, paper)
        reviewer, editor = normalize_message_participants(request, paper, reviewer, editor)
        reviewer, editor = resolve_message_participants(user, paper, reviewer, editor)

        if has_user_access_to_messages(user, paper, reviewer, editor):
            message = Message.objects.create(
                author=user,
                paper=paper,
                reviewer=reviewer,
                editor=editor,
                text=request.POST['message_text'],
            )

            send_message_notification_email(message)

            response.status_code = 200
        else:
            response.status_code = 400
    else:
        response.status_code = 401

    return response

def has_user_access_to_messages(user, paper, reviewer=None, editor=None):
    if paper is None or not user.is_authenticated:
        return False

    if reviewer is None and editor is None:
        return False

    if reviewer is not None and editor is not None:
        return False

    if reviewer is not None and reviewer not in paper.reviewers.all():
        return False

    if editor is not None and editor not in paper.editors.all():
        return False

    if user.is_staff or user == paper.author:
        return True

    if reviewer is not None and user == reviewer:
        return True

    if editor is not None and user == editor:
        return True

    return False


def get_selected_reviewer(request, paper):
    reviewer_id = request.POST.get('reviewer_id')
    if not reviewer_id:
        return None

    reviewer = User.objects.filter(pk=reviewer_id).first()
    if paper is None or reviewer is None or reviewer not in paper.reviewers.all():
        return None
    return reviewer


def get_selected_editor(request, paper):
    editor_id = request.POST.get('editor_id')
    if not editor_id:
        return None

    editor = User.objects.filter(pk=editor_id).first()
    if paper is None or editor is None or editor not in paper.editors.all():
        return None
    return editor


def resolve_message_participants(user, paper, reviewer=None, editor=None):
    if paper is None:
        return None, None

    if reviewer is not None or editor is not None:
        return reviewer, editor

    if user in paper.reviewers.all():
        return user, None

    if user in paper.editors.all():
        return None, user

    if user.is_staff or user == paper.author:
        if paper.reviewers.count() == 1 and paper.editors.count() == 0:
            return paper.reviewers.first(), None
        if paper.editors.count() == 1 and paper.reviewers.count() == 0:
            return None, paper.editors.first()

    return None, None


def normalize_message_participants(request, paper, reviewer=None, editor=None):
    if paper is None:
        return None, None

    reviewer_id = request.POST.get('reviewer_id')
    editor_id = request.POST.get('editor_id')

    # If both are set, prefer the explicitly selected tab identifier.
    if reviewer is not None and editor is not None:
        if editor_id:
            return None, editor
        if reviewer_id:
            return reviewer, None
        return None, None

    # Fallback for stale frontend payloads (e.g. only one id key sent).
    if reviewer is None and editor is None:
        participant_id = editor_id or reviewer_id
        if not participant_id:
            return None, None

        participant = User.objects.filter(pk=participant_id).first()
        if participant is None:
            return None, None

        if participant in paper.editors.all():
            return None, participant
        if participant in paper.reviewers.all():
            return participant, None

    return reviewer, editor
