from braces.views import CsrfExemptMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.http import FileResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from StronaProjektyKol.settings import SITE_NAME
from .filters import PaperFilter
from .forms import *


class PaperListView(LoginRequiredMixin, ListView):
    model = Paper
    template_name = 'papers/paper_list.html'
    context_object_name = 'papers'
    ordering = ['-updated_at']

    def get_context_data(self, **kwargs):
        context = super(PaperListView, self).get_context_data(**kwargs)

        context['site_name'] = 'papers'
        context['site_title'] = f'Referaty - {SITE_NAME}'
        context['filter'] = PaperFilter(self.request.GET, queryset=self.get_queryset())

        # for select input
        context['filter'].form['club'].field.widget.attrs['class'] = 'custom-select'
        context['filter'].form['approved'].field.widget.attrs['class'] = 'custom-select'
        context['filter'].form['reviewers_field'].field.widget.attrs['class'] = 'custom-select'
        context['filter'].form['reviews_count'].field.widget.attrs['class'] = 'custom-select'
        context['filter'].form['final_grade'].field.widget.attrs['class'] = 'custom-select'

        papers = context['filter'].qs.order_by('-updated_at')
        queryset_pks = ''
        for paper in papers:
            queryset_pks += f'&qspk={paper.pk}'
            paper.get_unread_messages = paper.get_unread_messages(self.request.user)

        context['queryset_pks'] = queryset_pks
        context['papers_length'] = papers.count()
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
        # FOR ADMIN
        if self.request.user.is_staff:
            return Paper.objects.all()
        # FOR REVIEWER
        if self.request.user.groups.filter(name='reviewer').exists():
            return Paper.objects.all().filter(reviewers=self.request.user)
        # FOR REGULAR USER
        return Paper.objects.all().filter(authors=self.request.user)


class PaperDetailView(LoginRequiredMixin, UserPassesTestMixin, CsrfExemptMixin, DetailView):
    login_url = 'login'
    model = Paper
    context_object_name = 'paper'

    def get_context_data(self, *args, **kwargs):
        context = super(PaperDetailView, self).get_context_data(*args, **kwargs)

        context['reviews'] = Review.objects.filter(paper=context['paper'])
        context['site_title'] = f'Informacje o referacie - {SITE_NAME}'
        paper_iter = 0

        GET_DATA = self.request.GET

        if 'id' in GET_DATA:
            paper_iter = int(GET_DATA['id'])
        if 'qspk' in GET_DATA:
            qs_list = [int(i) for i in GET_DATA.getlist('qspk')]
            queryset_pks = ''
            for itm in qs_list:
                queryset_pks += f'&qspk={itm}'
            context['queryset_pks'] = queryset_pks

            if 1 < paper_iter <= len(qs_list):
                var = Paper.objects.filter(pk=qs_list[paper_iter - 2]).first()
                if var is not None:
                    context['prev'] = var.pk
                    context['prev_id'] = paper_iter - 1

            if 1 <= paper_iter < len(qs_list):
                var = Paper.objects.filter(pk=qs_list[paper_iter]).first()
                if var is not None:
                    context['next'] = var.pk
                    context['next_id'] = paper_iter + 1

        return context

    def test_func(self):
        paper = self.get_object()
        if self.request.user in paper.authors.all() or self.request.user.groups.filter(name='reviewer').exists():
            return True
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
    template_name = 'papers/paper_add.html'
    model = Paper
    form_class = PaperCreationForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(PaperCreateView, self).get_context_data(**kwargs)
        context['site_name'] = 'papers'
        context['site_title'] = f'Nowy referat - {SITE_NAME}'
        # context['coAuthors'] = Formset('coAuthors')
        # context['files'] =  Formset('files', 'papers/upload_files_formset.html')

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
    template_name = 'papers/paper_edir.html'

    def test_func(self):
        paper = self.get_object()
        if self.request.user in paper.authors.all():
            return True
        return False

    def post(self, request, *args, **kwargs):
        paper = self.get_object()
        paper.updated_at = timezone.now()
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
    template_name = 'papers/paper_delete.html'
    success_url = '/papers'

    def test_func(self):
        paper = self.get_object()
        if self.request.user.pk == paper.original_author_id:
            return True
        return False

    def handle_no_permission(self):
        return redirect('paperList')


class ReviewDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Review
    context_object_name = 'review'
    template_name = 'papers/review_detail.html'

    def test_func(self):
        user = self.request.user
        paper = self.get_object().paper
        if user.is_staff or (user.groups.filter(
                name='reviewer').exists() and user in paper.reviewers.all()) or user in paper.authors.all() or user == self.get_object().author:
            return True
        return False

    def handle_no_permission(self):
        return redirect('paperList')


class ReviewListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Review
    context_object_name = 'reviews'
    template_name = 'papers/review_list.html'
    ordering = ['-updated_at']

    def get_queryset(self):
        return Review.objects.filter(author=self.request.user).all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = 'reviews'
        context['site_title'] = f'Recenzje - {SITE_NAME}'
        return context

    def test_func(self):
        user = self.request.user
        if user.is_staff or user.groups.filter(name='reviewer').exists():
            return True
        return False

    def handle_no_permission(self):
        return redirect('login')


class ReviewCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Review
    template_name = 'papers/review_add.html'
    success_url = '/papers'
    form_class = ReviewCreationForm

    def test_func(self):
        user = self.request.user
        paper = Paper.objects.get(pk=self.kwargs.get('paper'))

        if user in paper.authors.all() or (self.request.user.groups.filter(
                name='reviewer').exists() and not user.is_staff) or paper.reviewers.filter(pk=user.pk).count() == 0:
            return False
        return True

    def get_context_data(self, **kwargs):
        context = super(ReviewCreateView, self).get_context_data(**kwargs)
        context['paper'] = Paper.objects.get(pk=self.kwargs.get('paper'))
        return context

    def handle_no_permission(self):
        return redirect('paperList')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.paper = Paper.objects.get(pk=self.kwargs.get('paper'))
        return super(ReviewCreateView, self).form_valid(form)


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    template_name = 'papers/review_add.html'
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
    template_name = 'papers/review_delete.html'
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


class ReviewerAssignmentView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Paper
    template_name = 'papers/reviewer_assign.html'
    form_class = ReviewerAssignmentForm

    def form_valid(self, form):
        messages.success(self.request, 'Zapisano zmiany')
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


@csrf_exempt
def userReviewShow(request, **kwargs):
    user = request.user
    if not user.is_authenticated:
        return False

    paper = Paper.objects.get(pk=kwargs.get('paper'))
    reviewer = User.objects.get(pk=kwargs.get('reviewer'))
    if paper is None or reviewer is None or (
            user.groups.filter(name='reviewer').exists() and user not in paper.reviewers.all() and not user.is_staff):
        return HttpResponse(status=404)
    if not user.is_staff and not user.groups.filter(name='reviewer').exists() and user not in paper.authors.all():
        return HttpResponse(status=404)

    review = Review.objects.filter(author=reviewer, paper=paper).first()

    if review is None:
        if user == reviewer:
            return redirect('reviewCreate', kwargs['paper'])
        else:
            return render(request, template_name='papers/review_not_found.html')
    else:
        return redirect('reviewDetail', review.pk)
