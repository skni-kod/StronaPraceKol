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
        if not queryset:
            queryset = qs.all()
        return queryset


class PaperFilter(django_filters.FilterSet):

    title = CharFilter(field_name='title', lookup_expr='icontains', label='tytuł')
    keywords = MultiValueCharFilter(field_name='keywords', label='Słowa kluczowe oddzielone przecinkami',
                                    lookup_expr='icontains', widget=CSVWidget, help_text='')
    club = ModelChoiceFilter(queryset=StudentClub.objects.exclude(acronym='BRAK'), field_name='club', label='koło')

    class Meta:
        model = Paper
        fields = ['club']

