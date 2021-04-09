from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView

from .filters import PaperFilter
from .forms import *
from StronaProjektyKol.settings import SITE_NAME, SITE_DOMAIN, SITE_ADMIN_MAIL, SITE_ADMIN_PHONE


class PaperListView(LoginRequiredMixin, ListView):
    model = Paper
    template_name = 'papers/paper_list.html'
    context_object_name = 'papers'
    ordering = ['-last_edit_date']

    def get_context_data(self, **kwargs):

        context = super(PaperListView, self).get_context_data(**kwargs)
        context['site_name'] = 'papers'
        context['site_title'] = f'Referaty - {SITE_NAME}'
        context['filter'] = PaperFilter(self.request.GET, queryset=self.get_queryset())
        # for select input
        context['filter'].form['club'].field.widget.attrs['class'] = 'custom-select'

        papers = context['filter'].qs.order_by('-last_edit_date')
        paginator = Paginator(papers, 5)
        page = self.request.GET.get('page', 1)
        try:
            context['papers'] = paginator.page(page)
        except PageNotAnInteger:
            context['papers'] = paginator.page(1)
        except EmptyPage:
            context['papers'] = paginator.page(paginator.num_pages)
        return context

    def get_queryset(self):
        # FOR REVIEWER
        # if self.request.user.groups.filter(name='reviewer').exists():
        #     return Paper.objects.all().order_by('-last_edit_date')
        return Paper.objects.filter(authors=self.request.user)


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
    """
    Function allows logged in users to download a file if they have permission to
    :param request:
    :param pk: integer (id of a paper that the files belongs to)
    :param item: integer (id of a file user wants to download)
    :return:
    """
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

    def get_success_url(self):
        messages.success(self.request, f'Dodano referat')
        return str('/papers/')


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
        paper = self.get_object()
        paper.last_edit_date = timezone.now()
        paper.save()
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
        messages.success(self.request, f'Referat został zmieniony')
        paper = self.get_object()
        return str('/papers/paper/' + str(paper.pk) + '/')

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
    success_url = '/papers'
    form_class = ReviewCreationForm

    def test_func(self):
        paper = Paper.objects.get(pk=self.kwargs.get('pk'))
        if self.request.user not in paper.authors.all() and self.request.user.groups.filter(name='reviewer').exists():
            for review in paper.review_set.all():
                if review.author == self.request.user:
                    return False
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(ReviewCreateView, self).get_context_data(**kwargs)
        context['paper'] = Paper.objects.get(pk=self.kwargs.get('pk'))
        return context

    def handle_no_permission(self):
        return redirect('paperList')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.paper = Paper.objects.get(pk=self.kwargs.get('pk'))
        return super(ReviewCreateView, self).form_valid(form)


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    template_name = 'papers/add_review.html'
    form_class = ReviewCreationForm
    success_url = '/papers'

    def get_context_data(self, **kwargs):
        context = super(ReviewUpdateView, self).get_context_data(**kwargs)
        context['paper'] = Paper.objects.get(pk=self.kwargs.get('paper'))
        return context

    def test_func(self):
        review = self.get_object()
        if self.request.user == review.author:
            return True
        return False

    def handle_no_permission(self):
        return redirect('paperList')


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = 'papers/delete_review.html'
    success_url = '/papers'

    def test_func(self):
        review = self.get_object()
        if self.request.user == review.author:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(ReviewDeleteView, self).get_context_data(**kwargs)
        context['paper'] = Paper.objects.get(pk=self.kwargs.get('paper'))
        return context

    def handle_no_permission(self):
        return redirect('paperList')


class UserReviewListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Review
    template_name = 'papers/user_review_list.html'
    context_object_name = 'reviews'
    paginate_by = 5

    def test_func(self):
        if self.request.user.groups.filter(name='reviewer').exists():
            return True
        return False

    def get_queryset(self):
        return Review.objects.filter(author=self.request.user)

    def handle_no_permission(self):
        return redirect('paperList')

    def get_context_data(self, **kwargs):
        context = super(UserReviewListView, self).get_context_data(**kwargs)
        context['title'] = 'mojeRecenzje'
        return context


class ReviewerAssignmentView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'papers/reviewer_assignment.html'
    form_class = ReviewerAssignmentForm
    success_url = '/papers/assignreviewers/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['papers'] = Paper.objects.all()  # TODO(mystyk): add filter which papers are ready to be reviewed
        return context

    def test_func(self):
        # TODO(mystyk): Check if user is admin
        return True
