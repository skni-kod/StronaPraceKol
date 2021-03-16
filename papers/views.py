from .models import Paper, UploadedFile
from django.shortcuts import redirect
from django.http import FileResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.decorators import login_required
from .forms import PaperCreationForm, CoAuthorFormSet, UploadedFileFormSet
from django.db import transaction
from django.urls import reverse_lazy
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
    # Function used to ensure that user is allowed to download given file
    paper = Paper.objects.get(pk=pk)
    if request.user in paper.authors.all() or request.user.groups.filter(name='reviewer').exists():
        document = UploadedFile.objects.get(pk=item)
        response = FileResponse(document.file)
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(document.file.path)

        return response
    else:
        return redirect('paper-list')


class PaperCreateView(LoginRequiredMixin, CreateView):
    template_name = 'papers/add_paper.html'
    model = Paper
    form_class = PaperCreationForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(PaperCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['coAuthors'] = CoAuthorFormSet(self.request.POST)
            context['files'] = UploadedFileFormSet(self.request.POST, self.request.FILES)
        else:
            context['coAuthors'] = CoAuthorFormSet()
            context['files'] = UploadedFileFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        coAuthors = context['coAuthors']
        files = context['files']
        with transaction.atomic():
            form.instance.original_author_id = self.request.user.pk
            self.object = form.save()
            form.instance.authors.add(self.request.user)
            if coAuthors.is_valid():
                coAuthors.instance = self.object
                coAuthors.save()
            if files.is_valid():
                for f in self.request.FILES.getlist('uploadedfile_set-0-file'):
                    file_instance = UploadedFile(file=f, paper=self.object)
                    file_instance.save()
        return super(PaperCreateView, self).form_valid(form)






