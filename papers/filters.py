import django_filters
from .models import Paper, StudentClub
from django_filters import CharFilter, ModelChoiceFilter
from django_filters.constants import EMPTY_VALUES
from django_filters.widgets import CSVWidget


class MultiValueCharFilter(django_filters.BaseCSVFilter, django_filters.CharFilter):
    """
    Custom filter to accept multiple CharFilter strings provided using CSVWidget
    """
    def filter(self, qs, value):
        values = value or []
        queryset = None
        for value in values:
            if value in EMPTY_VALUES:
                return qs
            if self.distinct:
                qs = qs.distinct()
            lookup = '%s__%s' % (self.field_name, self.lookup_expr)
            if not queryset:
                queryset = self.get_method(qs)(**{lookup: value})
            else:
                queryset = queryset | self.get_method(qs)(**{lookup: value})
        if not queryset and len(value) == 0:
            queryset = qs.all()
        return queryset


class MultiValueUserFilter(django_filters.BaseCSVFilter, django_filters.CharFilter):
    """
    Custom filter to accept multiple CharFilter strings and compare them with papers' authors
    """

    def __init__(self, ref_field='last_name', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ref_field = ref_field

    def filter(self, qs, value):
        values = value or []
        queryset = None
        for value in values:
            if value in EMPTY_VALUES:
                return qs
            if self.distinct:
                qs = qs.distinct()
            if not queryset:
                if self.ref_field == 'first_name':
                    queryset = self.name_filter(qs, value)
                elif self.ref_field == 'last_name':
                    queryset = self.surname_filter(qs, value)
            else:
                if self.ref_field == 'first_name':
                    queryset = self.name_filter(queryset, value)
                elif self.ref_field == 'last_name':
                    queryset = self.surname_filter(queryset, value)
        if not queryset and len(values) == 0:
            queryset = qs.all()
        return queryset

    def name_filter(self, qs, name):
        return qs.filter(authors__first_name__icontains=name)

    def surname_filter(self, qs, surname):
        return qs.filter(authors__last_name__icontains=surname)


class PaperFilter(django_filters.FilterSet):

    title = CharFilter(field_name='title', lookup_expr='icontains', label='tytuł')
    keywords = MultiValueCharFilter(field_name='keywords', label='Słowa kluczowe oddzielone przecinkami',
                                    lookup_expr='icontains', widget=CSVWidget, help_text='')
    author_name = MultiValueUserFilter(ref_field='first_name', label='imiona autorów', widget=CSVWidget, help_text='')
    author_surname = MultiValueUserFilter(ref_field='last_name', label='nazwiska autorów', widget=CSVWidget, help_text='')
    club = ModelChoiceFilter(queryset=StudentClub.objects.exclude(acronym='BRAK'), field_name='club', label='koło')

    class Meta:
        model = Paper
        fields = ['club']

