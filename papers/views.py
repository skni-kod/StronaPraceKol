from .models import Paper, UploadedFile
from django.shortcuts import redirect
from django.http import FileResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.decorators import login_required
from .forms import PaperCreationForm
import os


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


class PaperDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
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


@login_required
def paper_file_download(request, pk, item):
    paper = Paper.objects.get(pk=pk)
    if request.user in paper.authors.all() or request.user.groups.filter(name='reviewer').exists():
        document = UploadedFile.objects.get(pk=item)
        response = FileResponse(document.file)
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(document.file.path)

        return response
    else:
        return redirect('paper-list')


class PaperCreateView(LoginRequiredMixin, CreateView):
    model = Paper
    template_name = 'papers/add_paper.html'
    form_class = PaperCreationForm
