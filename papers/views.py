from .models import Paper, UploadedFile
from django.shortcuts import redirect, render
from django.http import FileResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, FormView, View
from django.contrib.auth.decorators import login_required
from .forms import PaperCreationForm, FileUploadForm
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


class PaperCreateView(LoginRequiredMixin, View):
    template_name = 'papers/add_paper.html'

    def get(self, request, *args, **kwargs):
        paper_form = PaperCreationForm()
        file_form = FileUploadForm()
        context = {'paper_form': paper_form, 'file_form': file_form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        paper_form = PaperCreationForm(request.POST)
        file_form = FileUploadForm(request.POST, request.FILES)
        # TODO not sure about assigning values by that function
        paper_form.instance.original_author_id = request.user.id
        if paper_form.is_valid():
            paper_form.save()
            paper = paper_form.instance
            files = request.FILES.getlist('file')
            if file_form.is_valid():
                for f in files:
                    file_instance = UploadedFile(file=f, paper=paper)
                    file_instance.save()
            return redirect('paperList')
        else:
            paper_form = PaperCreationForm()
            file_form = FileUploadForm()
            context = {'paper_form': paper_form, 'file_form': file_form}

        return render(request, self.template_name, context)


class UploadTest(LoginRequiredMixin, FormView):
    file_form = FileUploadForm()
    template_name = 'papers/add_paper.html'


