import requests
from braces.views import CsrfExemptMixin
from django.contrib import messages
from urllib.parse import unquote
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.mail import EmailMultiAlternatives, BadHeaderError
from django.db import transaction
from django.utils.html import strip_tags
from django.http import FileResponse, HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.static import serve
from StronaProjektyKol.settings import SITE_NAME, BASE_DIR, SITE_ADMIN_MAIL, GOTENBERG_URL
from messaging.utils import send_paper_creation_notification_email
from .filters import PaperFilter
from .forms import *
import requests

STATEMENT_FILE = 'statement-file'

class PaperListView(LoginRequiredMixin, ListView):
    model = Paper
    template_name = 'papers/paper_list.html'
    context_object_name = 'papers'
    ordering = ['title']

    def get_context_data(self, **kwargs):
        context = super(PaperListView, self).get_context_data(**kwargs)

        context['site_name'] = 'papers'
        context['site_title'] = f'Artykuły - {SITE_NAME}'
        context['filter'] = PaperFilter(
            self.request.GET, queryset=self.get_queryset())

        papers = context['filter'].qs.order_by('title')
        queryset_pks = ''
        for paper in papers:
            queryset_pks += f'&q={paper.pk}'
            paper.get_unread_messages = len(
                paper.get_unread_messages(self.request.user))

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
        return Paper.objects.all().filter(author=self.request.user)


class PaperDetailView(LoginRequiredMixin, UserPassesTestMixin, CsrfExemptMixin, DetailView):
    login_url = 'login'
    model = Paper
    context_object_name = 'paper'

    def get_context_data(self, *args, **kwargs):
        context = super(PaperDetailView, self).get_context_data(**kwargs)

        context['reviews'] = Review.objects.filter(paper=context['paper'])
        context['site_title'] = f'Informacje o artykule - {SITE_NAME}'
        paper_iter = 0

        GET_DATA = self.request.GET

        if 'id' in GET_DATA and GET_DATA['id'] is not None:
            paper_iter = int(GET_DATA['id'])
        if 'q' in GET_DATA:
            qs_list = [int(i) for i in GET_DATA.getlist('q')]
            queryset_pks = ''
            for itm in qs_list:
                queryset_pks += f'&q={itm}'
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
        if self.request.user == paper.author or self.request.user.groups.filter(name='reviewer').exists():
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
    print("request", request, "pk", pk, "item", item)
    paper = Paper.objects.get(pk=pk)
    print("paper", paper)
    if request.user == paper.author or request.user.groups.filter(
            name='reviewer').exists() or request.user.is_staff:
        document = UploadedFile.objects.get(pk=item)
        print("document", document)
        filepath = str(BASE_DIR)+document.file.url
        print("filepath", unquote(filepath))
        return serve(request, os.path.basename(unquote(filepath)), os.path.dirname(unquote(filepath)))
    else:
        return redirect('paper-list')


class PaperCreateView(LoginRequiredMixin, CreateView):
    template_name = 'papers/paper_add.html'
    model = Paper
    form_class = PaperCreationForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(PaperCreateView, self).get_context_data(**kwargs)
        context['form'].fields['club'].empty_label = 'Wybierz koło naukowe'
        context['site_name'] = 'papers'
        context['site_title'] = f'Nowy artykuł - {SITE_NAME}'
        context['site_type'] = 'create'

        if self.request.POST:
            context['coAuthors'] = CoAuthorFormSet(self.request.POST)
            context['files'] = UploadFileFormSet(
                self.request.POST, self.request.FILES)
            context['statement'] = FileUploadForm(
                self.request.POST, self.request.FILES, prefix='statement')
        else:
            context['coAuthors'] = CoAuthorFormSet()
            context['files'] = UploadFileFormSet()
            context['statement'] = FileUploadForm(prefix='statement')

        context['statement'].fields['file'].required = False
        context['statement'].fields['file'].widget.attrs['multiple'] = False

        context['coAuthorsForm'] = render_to_string('papers/paper_add_author_formset.html',
                                                    {'formset': context['coAuthors']})

        context['filesForm'] = render_to_string('papers/upload_files_formset.html',
                                                {'formset': context['files']})

        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        co_authors = context['coAuthors']
        files = context['files']

        if not co_authors.is_valid():
            return self.form_invalid(form)


        with transaction.atomic():
            form.instance.author = self.request.user
            form.instance.author_percentage = co_authors.calculate_author_percentage()
            self.object = form.save()

            if co_authors.is_valid():
                co_authors.instance = self.object
                co_authors.save()

            if context['statement'].is_valid():
                statement_file = context['statement'].cleaned_data.get('file')
                if statement_file:
                    file_instance = UploadedFile(file=statement_file, paper=self.object)
                    file_instance.save()
                    self.object.statement = file_instance.pk
                    self.object.save()

            if files.is_valid():
                # receiced a list of file fields
                # each file field has a list of files
                # but file can be empty, so we need to check it
                for file_fields in self.request.FILES.lists():
                    if file_fields[0] == STATEMENT_FILE:
                        continue
                    for file_field in file_fields[1]:
                        if len(file_fields[1]) > 0:
                            file_instance = UploadedFile(
                                file=file_field, paper=self.object)
                            file_instance.save()

        send_paper_creation_notification_email(self.object)
        return super(PaperCreateView, self).form_valid(form)


    def get_success_url(self):
        messages.success(self.request, f'Dodano artykuł')
        return str('/papers/')


class PaperEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Paper
    form_class = PaperCreationForm
    template_name = 'papers/paper_add.html'

    def test_func(self):
        paper = self.get_object()
        if self.request.user == paper.author:
            return True
        return False

    def post(self, request, *args, **kwargs):
        paper = self.get_object()
        paper.updated_at = timezone.now()
        paper.save()

        for key in request.POST.items():
            if 'file-delete-' in key[0]:
                if len(key[1]) > 0:
                    UploadedFile.objects.filter(pk=key[1]).delete()

        return super(PaperEditView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PaperEditView, self).get_context_data(**kwargs)
        context['site_name'] = 'papers'
        context['site_title'] = f'Edytuj artykuł - {SITE_NAME}'
        context['site_type'] = 'edit'

        if self.request.POST:
            context['coAuthors'] = CoAuthorFormSet(self.request.POST, instance=self.object)
            context['files'] = UploadFileFormSet(self.request.POST, self.request.FILES)
            context['statement'] = FileUploadForm(self.request.POST, self.request.FILES, prefix='statement')
        else:
            context['coAuthors'] = CoAuthorFormSet(instance=self.object)
            context['files'] = UploadFileFormSet()
            context['statement'] = FileUploadForm(prefix='statement')

        context['statement'].fields['file'].required = False
        context['statement'].fields['file'].widget.attrs['multiple'] = False

        if self.object.statement:
            context['current_statement'] = UploadedFile.objects.filter(pk=self.object.statement).first()

        context['uploaded_files'] = UploadedFile.objects.filter(
            paper=self.get_object()).exclude(pk=self.get_object().statement)
        context['coAuthorsForm'] = render_to_string('papers/paper_add_author_formset.html',
                                                    {'formset': context['coAuthors']})
        context['filesForm'] = render_to_string('papers/upload_files_formset.html',
                                                {'formset': context['files']})

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        coAuthors = context['coAuthors']
        files = context['files']

        if not coAuthors.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            form.instance.author = self.request.user
            form.instance.author_percentage = coAuthors.calculate_author_percentage()
            self.object = form.save()
            if coAuthors.is_valid():
                coAuthors.instance = self.object
                coAuthors.save()

            
            if context['statement'].is_valid():
                statement_file = context['statement'].cleaned_data.get('file')
                if statement_file:
                    old_statement = UploadedFile.objects.filter(pk=self.object.statement).first()
                    file_instance = UploadedFile(file=statement_file, paper=self.object)
                    file_instance.save()
                    if old_statement:
                        old_statement.delete()
                    self.object.statement = file_instance.pk
                    self.object.save()

            if files.is_valid():
                for file_fields in self.request.FILES.lists():
                    if file_fields[0] == STATEMENT_FILE:
                        continue
                    for file_field in file_fields[1]:
                        file_instance = UploadedFile(
                            file=file_field, paper=self.object)
                        file_instance.save()
        return super(PaperEditView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, f'Artykuł został zmieniony')
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
        if self.request.user == paper.author:
            return True
        return False

    def handle_no_permission(self):
        return redirect('paperList')


class ReviewDetailView(CsrfExemptMixin, LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Review
    context_object_name = 'review'
    template_name = 'papers/review_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ReviewDetailView, self).get_context_data(**kwargs)
        context['grades'] = Grade.objects.all()
        return context

    def test_func(self):
        user = self.request.user
        paper = self.get_object().paper
        if user.is_staff or (user.groups.filter(
                name='reviewer').exists() and user in paper.reviewers.all()) or user == paper.author or user == self.get_object().author:
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
        for review in context['reviews']:
            review.paper.get_unread_messages = len(
                review.paper.get_unread_messages(self.request.user))
        return context

    def test_func(self):
        user = self.request.user
        if user.is_staff or user.groups.filter(name='reviewer').exists():
            return True
        return False

    def handle_no_permission(self):
        return redirect('login')


def send_review_notification_email(review):
    paper = review.paper
    reviewer = paper.reviewers.filter(pk=review.author.pk).first()

    recipients = []

    if paper.author.email:
        recipients.append(paper.author.email)

    for coauthor in paper.coauthor_set.all():
        if coauthor.email:
            recipients.append(coauthor.email)

    recipients = list(set(recipients))
    if not recipients:
        return

    context = {
        "paper": paper,
        "reviewer": reviewer,
        "review": review,
    }

    subject = f"Nowa recenzja dla artykułu: {paper.title[:50]}..."
    html_content = render_to_string("emails/review_notification.html", context)
    plain_text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=plain_text_content,
        from_email=SITE_ADMIN_MAIL,
        to=[SITE_ADMIN_MAIL],
        bcc=recipients,
        headers={'Reply-To': SITE_ADMIN_MAIL}
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()

class ReviewCreateView(CsrfExemptMixin, LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Review
    template_name = 'papers/review_add.html'
    success_url = reverse_lazy('reviewSuccess')
    form_class = ReviewCreationForm
    success_message = "Poprawnie dodano!"

    def test_func(self):
        user = self.request.user
        paper = Paper.objects.get(pk=self.kwargs.get('paper'))

        if user in [itm.author for itm in paper.review_set.all()]:
            return False
        if user == paper.author or (self.request.user.groups.filter(
                name='reviewer').exists() and not user.is_staff) or paper.reviewers.filter(pk=user.pk).count() == 0:
            return False
        return True

    def get_context_data(self, **kwargs):
        context = super(ReviewCreateView, self).get_context_data(**kwargs)
        context['paper'] = Paper.objects.get(pk=self.kwargs.get('paper'))
        return context

    def handle_no_permission(self):
        return render(self.request, template_name='papers/review_not_found.html')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.paper = Paper.objects.get(pk=self.kwargs.get('paper'))

        response = super(ReviewCreateView, self).form_valid(form)

        send_review_notification_email(self.object)

        return response


class ReviewUpdateView(SuccessMessageMixin, CsrfExemptMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    template_name = 'papers/review_add.html'
    form_class = ReviewCreationForm
    success_url = reverse_lazy('reviewSuccess')
    success_message = "Poprawnie wprowadzono zmiany"

    def get_context_data(self, **kwargs):
        context = super(ReviewUpdateView, self).get_context_data(**kwargs)
        context['paper'] = super().get_object().paper
        return context

    def test_func(self):
        review = self.get_object()
        if self.request.user == review.author:
            return True
        return False

    def handle_no_permission(self):
        return render(self.request, template_name='papers/review_not_found.html')


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, CsrfExemptMixin, DeleteView):
    model = Review
    template_name = 'papers/review_delete.html'
    success_url = reverse_lazy('reviewSuccess')
    success_message = 'Usunięto recenzję'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ReviewDeleteView, self).delete(request, *args, **kwargs)

    def test_func(self):
        review = self.get_object()
        if self.request.user == review.author:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(ReviewDeleteView, self).get_context_data(**kwargs)
        return context

    def handle_no_permission(self):
        return render(self.request, template_name='papers/review_not_found.html')


class ReviewSuccessView(LoginRequiredMixin, CsrfExemptMixin, TemplateView):
    template_name = 'papers/review_success.html'


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

class ReviewPDFView(LoginRequiredMixin, UserPassesTestMixin, SingleObjectMixin, View):
    model = Review

    def test_func(self):
        try:
            review = self.get_object()
            return self.request.user == review.author
        except (Review.DoesNotExist, Http404):
                return False
   
    def handle_no_permission(self):
        return redirect('paperList')

    def get(self, request, pk):
        review = self.get_object()
        html = render_to_string('papers/review_pdf.html', {'review': review, 'questions': review.get_questions_with_answers()})
        
        try:
            response = requests.post(
                f"{GOTENBERG_URL}/forms/chromium/convert/html",
                files={'file': ('index.html', html, 'text/html')},
                timeout=10
            )

            if response.status_code != 200:
                return HttpResponse("Błąd generowania PDF", status=500)

            pdf_response = HttpResponse(
                response.content,
                content_type='application/pdf'
            )
            pdf_response['Content-Disposition'] = f'inline; filename="review_{pk}.pdf"'
            return pdf_response
        
        except:
            return HttpResponse("Usługa generowania PDF jest chwilowo niedostępna.", status=503) 
        
@csrf_exempt
def userReviewShow(request, **kwargs):
    user = request.user
    if not user.is_authenticated:
        return False

    paper = Paper.objects.get(pk=kwargs.get('paper'))
    reviewer = User.objects.get(pk=kwargs.get('reviewer'))
    if paper is None or reviewer is None or (
            not user.groups.filter(name='reviewer').exists() and user != paper.author and not user.is_staff):
        return HttpResponse(status=404)
    if not user.is_staff and not user.groups.filter(name='reviewer').exists() and user != paper.author:
        return HttpResponse(status=404)

    review = Review.objects.filter(author=reviewer, paper=paper).first()

    if review is None:
        if user == reviewer:
            return redirect('reviewCreate', paper.pk)
        else:
            return render(request, template_name='papers/review_not_found.html')
    else:
        return redirect('reviewDetail', review.pk)
      
@login_required
def paper_pdf_form_view(request, pk):
    paper = Paper.objects.get(pk=pk)
    
    if request.user != paper.author and not request.user.is_staff:
        return redirect('paperDetail', pk=pk)
    
    coAuthors_count = paper.coauthor_set.count() + 1
    
    formset_prefix = 'authors'

    if request.method == 'POST':
        formset = AuthorPersonalDataFormSet(request.POST, prefix=formset_prefix)
        if formset.is_valid():
            authors_data = []
            for form in formset:
                if form.cleaned_data:
                    authors_data.append({
                        'name': form.cleaned_data.get('name', ''),
                        'surname': form.cleaned_data.get('surname', ''),
                        'pesel': form.cleaned_data.get('pesel', ''),
                        'address': form.cleaned_data.get('address', ''),
                    })
            
            request.session['pdf_authors_data'] = authors_data
            request.session.modified = True
            
            return redirect('paperStatementPdf', pk=pk)
    else:
        initial_data = [
            {
                'name': paper.author.first_name,
                'surname': paper.author.last_name,
                'pesel': '',
                'address': '',
            }
        ]

        for coauthor in paper.coauthor_set.all():
            initial_data.append({
                'name': coauthor.name,
                'surname': coauthor.surname,
                'pesel': '',
                'address': '',
            })

        while len(initial_data) < coAuthors_count:
            initial_data.append({})

        formset = AuthorPersonalDataFormSet(
            prefix=formset_prefix,
            initial=initial_data
        )
    
    context = {
        'object': paper,
        'formset': formset,
        'site_title': f'Dane autora - {SITE_NAME}',
        'site_name': 'papers',
    }
    
    return render(request, 'papers/paper_pdf_form.html', context)


@login_required
def paper_statement_pdf(request, pk):
    paper = Paper.objects.get(pk=pk)

    if request.user != paper.author and not request.user.is_staff:
        return redirect('paperDetail', pk=pk)

    authors_data = request.session.get('pdf_authors_data') or []

    contributors = []
    if authors_data:
        if authors_data:
            entry = authors_data[0]
            name = f"{entry.get('name', '').strip()} {entry.get('surname', '').strip()}".strip()
            contributors.append({
                'name': name or 'Autor',
                'pesel': entry.get('pesel', ''),
                'address': entry.get('address', ''),
                'percentage': paper.author_percentage,
            })
        
        coAuthors = paper.coauthor_set.all()
        for idx, coauthor in enumerate(coAuthors):
            if idx + 1 < len(authors_data):
                entry = authors_data[idx + 1]
                name = f"{entry.get('name', '').strip()} {entry.get('surname', '').strip()}".strip()
                contributors.append({
                    'name': name or coauthor.name,
                    'pesel': entry.get('pesel', ''),
                    'address': entry.get('address', ''),
                    'percentage': coauthor.percentage,
                })
    else:
        contributors.append({
            'name': f"{paper.author.first_name} {paper.author.last_name}".strip() or paper.author.username,
            'pesel': '',
            'address': '',
            'percentage': paper.author_percentage,
        })
        for coauthor in paper.coauthor_set.all():
            contributors.append({
                'name': f"{coauthor.name} {coauthor.surname}".strip(),
                'pesel': '',
                'address': '',
                'percentage': coauthor.percentage,
            })
    
    for idx, contributor in enumerate(contributors):
        other_authors = [c for i, c in enumerate(contributors) if i != idx]
        contributor['other_authors'] = other_authors

    html = render_to_string(
        'papers/paper_statement.html',
        {
            'paper': paper,
            'contributors': contributors,
        },
    )

    url = f"{GOTENBERG_URL}/forms/chromium/convert/html"
    files = {
        'index.html': ('index.html', html.encode('utf-8'), 'text/html'),
    }

    try:
        response = requests.post(url, files=files, timeout=30)
        response.raise_for_status()
    except requests.RequestException:
        return HttpResponse('Błąd generowania PDF', status=502)

    http_response = HttpResponse(response.content, content_type='application/pdf')
    http_response['Content-Disposition'] = 'inline; filename="oswiadczenie.pdf"'
    return http_response
