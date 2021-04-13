import django_filters
from django.db.models import Count, Q
from operator import and_, or_
from functools import reduce
from django_filters import CharFilter, ModelChoiceFilter, ChoiceFilter
from django_filters.constants import EMPTY_VALUES
from django_filters.widgets import CSVWidget

from .models import Paper, StudentClub, Review, Grade
from django.contrib.auth.models import User

from pprint import pprint

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
    REVIEWERS_CHOICE = {
        ('0', 'Nie przydzielone'),
        ('1', '1 przydzielony'),
        ('2', '2 przydzielonych')
    }

    STATUS_CHOICE = {
        ('True', 'Gotowy'),
        ('False', 'W przygotowaniu')
    }

    REVIEWS_CHOICE = {
        ('0', 'Brak'),
        ('1', 'Jedna'),
        ('2', 'Dwie')
    }

    FINAL_GRADE_CHOICE = [(obj.value,obj.name) for obj in Grade.objects.filter(tag='final_grade')]

    title = CharFilter(field_name='title', lookup_expr='icontains', label='Tytuł', help_text='Tytuł referatu')

    keywords = MultiValueCharFilter(field_name='keywords', label='Słowa kluczowe',
                                    lookup_expr='icontains', widget=CSVWidget, help_text='Słowa oddzielone przecinkiem')

    author_surname = MultiValueUserFilter(ref_field='last_name', label='Nazwiska autorów', widget=CSVWidget,
                                          help_text='Oddzielone przecinkiem', method='author_surname_func')

    club = ModelChoiceFilter(queryset=StudentClub.objects.exclude(acronym='Brak'), field_name='club',
                             label='Koło naukowe')

    reviewer_surname = MultiValueUserFilter(label='Nazwiska recenzentów', widget=CSVWidget, method='reviewers_lastname',
                                            help_text='Oddzielone przecinkiem')

    approved = ChoiceFilter(choices=STATUS_CHOICE, field_name='approved', label='Status', method='is_approved')

    reviewers_field = ChoiceFilter(choices=REVIEWERS_CHOICE, field_name='reviewers_check',
                                   label='Przydzielonych recenzentów',
                                   method='reviewers_check')

    reviews_count = ChoiceFilter(choices=REVIEWS_CHOICE, field_name='reviews_count', label='Wystawionych recenzji',
                                 method='reviews_count_func')

    final_grade = ChoiceFilter(choices=FINAL_GRADE_CHOICE, field_name='final_grade', label='Ocena końcowa',
                               method='final_grade_func')

    def author_surname_func(self,queryset, val1, val2):
        return queryset.filter(reduce(or_, [Q(authors__last_name__icontains=c) for c in val2])).distinct()

    def is_approved(self, queryset, val1, val2):
        return queryset.filter(approved=val2)

    def reviewers_check(self, queryset, val1, val2):
        return queryset.annotate(reviewers_num=Count('reviewers')).filter(reviewers_num=val2)

    def final_grade_func(self,queryset, val1, val2):
        return queryset.filter(Q(reviews__final_grade__value=val2)).distinct()
        # to_exclude = []
        # for itm in queryset.all():
        #     if Review.objects.filter(paper__id=itm.id, final_grade__value=val2).count() == 0:
        #         to_exclude.append(itm)
        #
        # return queryset.filter(~Q(id__in=[obj.id for obj in to_exclude]))

    def reviewers_lastname(self, queryset, val1, val2):
        to_exclude = []
        for itm in queryset.all():
            for val in val2:
                if itm.reviewers.filter(last_name__icontains=val):
                    break
            else:
                to_exclude.append(itm)

        return queryset.filter(~Q(id__in=[obj.id for obj in to_exclude]))

    def reviews_count_func(self, queryset, val1, val2):
        to_exclude = []
        val2 = int(val2)
        for itm in queryset.all():
            if not Review.objects.filter(paper__id=itm.id).count() == val2:
                to_exclude.append(itm)

        return queryset.filter(~Q(id__in=[obj.id for obj in to_exclude]))

    class Meta:
        model = Paper
        fields = ['club', 'approved', 'reviewers_field', 'reviewer_surname', 'reviews_count', 'final_grade']
