from django.utils import timezone
from .models import UserDetail


class UpdateLastActivityMiddleware:
    """
    Middleware that keeps track when each user was last seen on the page
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        assert hasattr(request, 'user'), 'The UpdateLastActivityMiddleware requires authentication middleware to be installed.'
        if request.user.is_authenticated:
            userLastSeen = UserDetail.objects.filter(user=request.user)
            if userLastSeen:
                userLastSeen.update(last_seen=timezone.now())
            else:
                userLastSeen.create(user=request.user)
        response = self.get_response(request)
        return response

