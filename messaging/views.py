from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from papers.models import Review, Message, MessageSeen


class TestView(TemplateView):
    template_name = "messaging/messagebox.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        review = Review.objects.filter(id=self.kwargs['pk']).first()
        if review is None:
            return context

        context['username'] = self.request.user.username
        context['review_id'] = self.kwargs['pk']
        context['unseen'] = len(get_unseen_messages(user=self.request.user, review=review))
        return context


@csrf_exempt
def render_message(request):
    return render(request, 'messaging/message.html', {
        'type': request.POST['type'],
    })


@csrf_exempt
def get_message(request):
    user = request.user
    review = Review.objects.filter(pk=request.POST['review_id']).first()

    if has_user_access_to_messages(user, review):
        last_message_id = int(request.POST['last_message_id'])
        messages = Message.objects.filter(review=review).order_by('add_date')
        data = dict()
        for message in messages:
            if last_message_id >= message.id:
                continue

            tmp = {'author': f'{message.author.username}',
                   'author_name': f'{message.author.first_name} {message.author.last_name}',
                   'date': f'{message.add_date.strftime("%d %b %H:%M")}', 'text': f'{message.text}',
                   'id': f'{message.id}'}
            data[message.pk] = tmp

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
        review = Review.objects.filter(pk=request.POST['review_id']).first()
        if has_user_access_to_messages(user, review):
            Message.objects.create(
                author=user,
                review=review,
                text=request.POST['message_text'],
            )
            response.status_code = 200
        else:
            response.status_code = 400
    else:
        response.status_code = 401

    return response


# TODO:
def has_user_access_to_messages(user, review):
    if review is None:
        return False

    if user.is_authenticated:
        if review.author == user:
            return True
        if user in review.paper.authors.all():
            return True

    else:
        return False


def get_unseen_messages(user, review):
    messages = Message.objects.filter(review=review)
    ret = []
    for message in messages:
        if message.author == user:
            continue
        if MessageSeen.objects.filter(message=message, reader=user).first() is None:
            ret.append(message)
    return ret
