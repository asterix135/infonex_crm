from django.views.generic import TemplateView
from crm.models import Person
from crm.constants import GEO_CHOICES, CAT_CHOICES, DIV_CHOICES

class Index(TemplateView):
    template_name = 'marketing/index.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        records = Person.objects.all()[:100]
        context['records'] = records
        context['geo_choices'] = GEO_CHOICES
        context['cat_choices'] = CAT_CHOICES
        context['div_choices'] = DIV_CHOICES
        return context
