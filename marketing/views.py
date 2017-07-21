from time import strftime

from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, TemplateView

from crm.models import Person, Changes
from crm.views import add_change_record
from crm.constants import GEO_CHOICES, CAT_CHOICES, DIV_CHOICES


class Add(TemplateView):
    template_name = 'marketing/index_addins/table_row.html'

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        self._person = Person(
            date_created=timezone.now(),
            created_by=request.user,
            date_modified=timezone.now(),
            modified_by=request.user,
        )
        self._person.save()
        context = self.get_context_data(**kwargs)
        return super(Add, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(Add, self).get_context_data(**kwargs)
        context['record'] = self._person
        context['geo_choices'] = GEO_CHOICES
        context['cat_choices'] = CAT_CHOICES
        context['div_choices'] = DIV_CHOICES
        return context


class Delete(View):

    def get(self, request, *args, **kwargs):
        raise Http404()

    def post(self, request, *args, **kwargs):
        person = get_object_or_404(Person, pk=request.POST['record_id'])
        pk = person.pk
        Changes.objects.filter(orig_id=pk).delete()
        if person.has_registration_history():
            add_change_record(person, 'delete')
        person.delete()
        return HttpResponse(status=200)


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


class UpdatePerson(View):

    def get(self, request, *args, **kwargs):
        raise Http404()

    def post(self, request, *args, **kwargs):
        person = get_object_or_404(Person, pk=request.POST['record_id'])
        update_field = request.POST['field']
        new_value = request.POST['new_value']
        old_value = getattr(person, update_field)
        if new_value in ('true', 'false') and old_value in (True, False):
            new_value = new_value == 'true'
        if new_value != old_value:
            setattr(person, update_field, new_value)
            person.date_modified = timezone.now()
            person.modified_by = request.user
            person.save()
        person_vals = {
            'date_modified': person.date_modified.strftime('%m/%d/%Y'),
            'state_prov': person.state_prov(),
        }
        return JsonResponse(person_vals)
