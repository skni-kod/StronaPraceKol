from .models import Paper, UploadedFile, Review
from django.shortcuts import redirect
from django.http import FileResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from .forms import *
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
        return redirect('paperList')


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


class PaperEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Paper
    form_class = PaperEditForm
    template_name = 'papers/change_paper.html'

    def test_func(self):
        paper = self.get_object()
        if self.request.user in paper.authors.all():
            return True
        return False

    def post(self, request, *args, **kwargs):
        if 'send-new-files' in request.POST:
            new_files = FileAppendForm(self.request.POST, self.request.FILES)
            files = request.FILES.getlist('file')
            if new_files.is_valid():
                for f in files:
                    file_instance = UploadedFile(file=f, paper=self.get_object())
                    file_instance.save()
            return HttpResponseRedirect(request.path_info)
        elif 'delete-file' in request.POST:
            filePK = request.POST.get('file-pk')
            UploadedFile.objects.filter(pk=filePK).delete()
            return HttpResponseRedirect(request.path_info)
        else:
            return super(PaperEditView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PaperEditView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['coAuthors'] = CoAuthorFormSet(self.request.POST, instance=self.object)
            context['files'] = FileAppendForm(self.request.POST, self.request.FILES)
        else:
            context['coAuthors'] = CoAuthorFormSet(instance=self.object)
            context['files'] = FileAppendForm()
        context['uploaded_files'] = UploadedFile.objects.filter(paper=self.get_object())
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        coAuthors = context['coAuthors']
        with transaction.atomic():
            self.object = form.save()
            if coAuthors.is_valid():
                coAuthors.instance = self.object
                coAuthors.save()
        return super(PaperEditView, self).form_valid(form)

    def get_success_url(self):
        return self.request.path_info

    def handle_no_permission(self):
        return redirect('paperList')


class PaperDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Paper
    template_name = 'papers/delete_paper.html'
    success_url = '/papers'

    def test_func(self):
        paper = self.get_object()
        if self.request.user.pk == paper.original_author_id:
            return True
        return False

    def handle_no_permission(self):
        return redirect('paperList')


class ReviewListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Review
    context_object_name = 'reviews'
    template_name = 'papers/review_list.html'

    def get_queryset(self):
        paper = Paper.objects.get(pk=self.kwargs.get('pk'))
        return Review.objects.filter(paper=paper)

    def get_context_data(self, **kwargs):
        context = super(ReviewListView, self).get_context_data(**kwargs)
        context['paper'] = Paper.objects.get(pk=self.kwargs.get('pk'))
        return context

    def test_func(self):
        paper = Paper.objects.get(pk=self.kwargs.get('pk'))
        if self.request.user.groups.filter(name='reviewer').exists() or self.request.user in paper.authors.all():
            return True
        return False

    def handle_no_permission(self):
        return redirect('paperList')


class ReviewCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Review
    template_name = 'papers/add_review.html'
    success_url = '/papers'  # TODO this might be change if we decide what is best
    form_class = ReviewCreationForm

    def test_func(self):
        paper = Paper.objects.get(pk=self.kwargs.get('pk'))
        if self.request.user not in paper.authors.all() and self.request.user.groups.filter(name='reviewer').exists():
            for review in paper.review_set.all():
                if review.author == self.request.user:
                    return False
            return True
        return False

    def handle_no_permission(self):
        return redirect('paperList')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.paper = Paper.objects.get(pk=self.kwargs.get('pk'))
        return super(ReviewCreateView, self).form_valid(form)



