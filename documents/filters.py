import django_filters
from django_filters import CharFilter, ModelChoiceFilter, ChoiceFilter
from django_filters.constants import EMPTY_VALUES


from .models import Document
from papers.models import StudentClub


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
        if not queryset and len(values) == 0:
            queryset = qs.all()
        return queryset


class DocumentFilter(django_filters.FilterSet):
    STATUS_CHOICE = {
        ('True', 'Gotowy do przesłania'),
        ('False', 'W przygotowaniu')
    }

    name = CharFilter(field_name='name', lookup_expr='icontains', label='Nazwa', help_text='Nazwa dokumentu')

    club = ModelChoiceFilter(queryset=StudentClub.objects.exclude(name='Brak'), field_name='club',
                             label='Koło naukowe')

    ready = ChoiceFilter(choices=STATUS_CHOICE, field_name='ready', label='Gotowość', method='is_ready')

    def is_ready(self, queryset, val1, val2):
        return queryset.filter(ready=val2).distinct()

    class Meta:
        model = Document
        fields = ['name', 'club', 'ready']
