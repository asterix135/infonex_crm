"""
Implements django-filters class objects
"""
import django_filters
from .models import Person
from django.db import models

class PersonFilter(django_filters.FilterSet):
    date_modified = django_filters.DateTimeFilter(lookup_type='lte')
    filter_overrides = {
        models.CharField: {
            'filter_class': django_filters.CharFilter,
            'extra': lambda f: {
                'lookup_type': 'icontains',
            }
        }
    }

    class Meta:
        model = Person
        fields = ['name', 'title',
                  'company', 'date_modified']
        order_by = True
