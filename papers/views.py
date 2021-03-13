from .models import Paper
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView


class PaperListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Paper
    template_name = 'papers/paper_list.html'
    context_object_name = 'papers'
    ordering = ['-last_edit_date']

    def get_queryset(self):
        if self.request.user.groups.filter(name='reviewer').exists():
            return Paper.objects.all().order_by('-last_edit_date')
        return Paper.objects.filter(authors=self.request.user).order_by('-last_edit_date')


class PaperDetailView(LoginRequiredMixin, UserPassesTestMixin,DetailView):
    login_url = 'login'
    model = Paper
    context_object_name = 'paper'

    def test_func(self):
        paper = self.get_object()
        if self.request.user in paper.authors.all() or self.request.user.groups.filter(name='reviewer').exists():
            return True
        else:
            return False

    def handle_no_permission(self):
        return redirect('paper-list')
