import os
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.views.static import serve
from braces.views import CsrfExemptMixin
from django.shortcuts import redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from StronaProjektyKol.settings import BASE_DIR, SITE_NAME
from .filters import DocumentFilter
from .forms import *
from .models import Document, UploadedFile


class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['site_name'] = 'documents'
        context['site_title'] = f'Dokumenty - {SITE_NAME}'

        context['filter'] = DocumentFilter(self.request.GET, queryset=self.get_queryset())

        documents = context['filter'].qs.order_by('-created_at')

        context['documents_length'] = documents.count()

        paginator = Paginator(documents, 5)
        page = self.request.GET.get('page', 1)
        try:
            context['documents'] = paginator.page(page)
        except PageNotAnInteger:
            context['documents'] = paginator.page(1)
        except EmptyPage:
            context['documents'] = paginator.page(paginator.num_pages)

        return context

    def get_queryset(self):
        # FOR ADMIN
        if self.request.user.is_staff:
            return Document.objects.all()
        # FOR REGULAR USER
        return Document.objects.all().filter(author=self.request.user)


class DocumentDetailView(LoginRequiredMixin, UserPassesTestMixin, CsrfExemptMixin, DetailView):
    login_url = 'login'
    model = Document
    context_object_name = 'document'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = f'Informacje o dokumencie - {SITE_NAME}'

        return context

    def test_func(self):
        document = self.get_object()
        if self.request.user == document.author or self.request.user.groups.filter(name='reviewer').exists()\
                or self.request.user.is_staff:
            return True
        else:
            return False

    def handle_no_permission(self):
        return redirect('documentList')


@login_required
def document_file_download(request, pk, item):
    """
    Function allows logged in users to download a file if they have permission to
    :param request:
    :param pk: integer (id of a paper that the files belongs to)
    :param item: integer (id of a file user wants to download)
    :return:
    """
    document = Document.objects.get(pk=pk)
    if request.user == document.author or request.user.groups.filter(
            name='reviewer').exists() or request.user.is_staff:
        document = UploadedFile.objects.get(pk=item)
        filepath = str(BASE_DIR)+document.file.url
        return serve(request, os.path.basename(filepath), os.path.dirname(filepath))
    else:
        return redirect('documentList')


class DocumentCreateView(LoginRequiredMixin, CreateView):
    template_name = 'documents/document_add.html'
    model = Document
    form_class = DocumentCreationForm
    success_url = '/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(DocumentCreateView, self).get_context_data(**kwargs)
        context['form'].fields['club'].empty_label = 'Wybierz koło naukowe'
        context['site_name'] = 'documents'
        context['site_title'] = f'Nowy dokument - {SITE_NAME}'
        context['site_type'] = 'create'

        if self.request.POST:
            context['files'] = UploadFileFormSet(self.request.POST, self.request.FILES)
        else:
            context['files'] = UploadFileFormSet()

        context['filesForm'] = render_to_string('papers/upload_files_formset.html',
                                                {'formset': context['files']})

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        files = context['files']
        with transaction.atomic():
            form.instance.author = self.request.user
            form.save()
            self.object = form.save()

            if files.is_valid():
                for file_fields in self.request.FILES.lists():
                    for file_field in file_fields[1]:
                        if len(file_fields[1]) > 0:
                            file_instance = UploadedFile(
                                file=file_field, document=self.object)
                            file_instance.save()
                            if file_fields[0] == 'file':
                                self.object.statement = file_instance.pk
                                self.object.save()

        return super(DocumentCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, f'Dodano dokument')
        return str('/documents/')


class DocumentEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Document
    form_class = DocumentCreationForm
    template_name = 'documents/document_add.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        document = self.get_object()
        if self.request.user == document.author:
            return True
        return False

    def post(self, request, *args, **kwargs):

        for key in request.POST.items():
            if 'file-delete' in key[0]:
                if len(key[1]) > 0:
                    UploadedFile.objects.filter(pk=key[1]).delete()

        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DocumentEditView, self).get_context_data(**kwargs)
        context['site_name'] = 'documents'
        context['site_title'] = f'Edytuj dokument - {SITE_NAME}'
        context['site_type'] = 'edit'

        if self.request.POST:
            context['files'] = UploadFileFormSet(self.request.POST, self.request.FILES)
        else:
            context['files'] = UploadFileFormSet()

        context['uploaded_files'] = UploadedFile.objects.filter(
            document=self.get_object())

        context['filesForm'] = render_to_string('papers/upload_files_formset.html',
                                                {'formset': context['files']})

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        files = context['files']
        with transaction.atomic():
            form.instance.author = self.request.user
            form.save()
            self.object = form.save()

            if files.is_valid():
                for file_fields in self.request.FILES.lists():
                    for file_field in file_fields[1]:
                        if len(file_fields[1]) > 0:
                            file_instance = UploadedFile(
                                file=file_field, document=self.object)
                            file_instance.save()
                            if file_fields[0] == 'file':
                                self.object.statement = file_instance.pk
                                self.object.save()

        return super(DocumentEditView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, f'Dokument został zmieniony')
        document = self.get_object()
        return str('/documents/document/' + str(document.pk) + '/')

    def handle_no_permission(self):
        return redirect('documentList')


class DocumentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Document
    template_name = 'documents/document_delete.html'
    success_url = '/documents'

    def test_func(self):
        document = self.get_object()
        if self.request.user == document.author:
            return True
        return False

    def handle_no_permission(self):
        return redirect('documentList')
