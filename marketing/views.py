from time import strftime

from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, TemplateView

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


class Index(ListView):
    template_name = 'marketing/index.html'
    context_object_name = 'records'
    queryset = Person.objects.all()
    paginate_by=250

    def _generate_pagination_list(self, context):
        paginator = context['paginator']
        page_obj = context['page_obj']
        page_num = page_obj.number
        last_page = paginator.num_pages
        pagination_list = [1,]

        # pre-page numbers
        if page_num > 500:
            start_num = page_num % 500
            start_num += 500 if start_num == 0 else 0
            while start_num < page_num:
                pagination_list.append(start_num)
                start_num += 500
            pagination_list.append(page_num - 100)
            pagination_list.append(page_num - 10)
        elif page_num > 100:
            start_num = page_num % 100
            start_num += 100 if start_num == 0 else 0
            while start_num < page_num:
                pagination_list.append(start_num)
                start_num += 100
            pagination_list.append(page_num - 10)
        elif page_num > 50:
            pagination_list.append(page_num-50)
            pagination_list.append(page_num - 10)
        elif page_num > 10:
            start_num = page_num % 10
            start_num += 10 if start_num == 0 else 0
            while start_num < page_num:
                pagination_list.append(start_num)
                start_num += 10
        for i in range (page_num-5, page_num):
            if i > 1:
                pagination_list.append(i)

        # post-page numbers
        for i in range(page_num + 1, page_num + 6):
            if i < last_page:
                pagination_list.append(i)
        if last_page - page_num > 500:
            pagination_list.append(page_num + 10)
            pagination_list.append(page_num + 100)
            start_num = page_num + 500
            while start_num < last_page:
                pagination_list.append(start_num)
                start_num += 500
        elif last_page - page_num > 100:
            pagination_list.append(page_num + 10)
            start_num = page_num + 100
            while start_num < last_page:
                pagination_list.append(start_num)
                start_num += 100
        elif last_page - page_num > 50:
            pagination_list.append(page_num + 10)
            pagination_list.append(page_num + 50)
        elif last_page - page_num > 10:
            start_num = page_num + 10
            while start_num < last_page:
                pagination_list.append(start_num)
                start_num += 10

        if last_page > 1:
            pagination_list.append(last_page)

        return pagination_list

    def get_ordering(self):
        """
        Return the field or fields to use for ordering the queryset.
        Overrides default method
        """
        self.order = self.request.GET.get('order', 'asc')
        sort_by = self.request.GET.get('sort_by', None)
        if sort_by and self.order == 'desc':
            sort_by = '-' + sort_by
        return self.ordering

    def get_paginate_by(self, queryset):
        return super(Index, self).get_paginate_by(queryset)

    def get_queryset(self):
        return super(Index, self).get_queryset()

    def paginate_queryset(self, queryset, page_size):
        """
        Paginate the queryset, if needed.
        Override default method to go to first or last page if out of bounds
        """
        paginator = self.get_paginator(
            queryset, page_size, orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty())
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(_("Page is not 'last', nor can it be converted to an int."))
        if page_number < 1:
            page_number = 1
        if page_number > paginator.num_pages:
            page_number = paginator.num_pages
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
                'page_number': page_number,
                'message': str(e)
            })

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['geo_choices'] = GEO_CHOICES
        context['cat_choices'] = CAT_CHOICES
        context['div_choices'] = DIV_CHOICES
        if context['is_paginated']:
            context['pagination_list'] = self._generate_pagination_list(context)
        context['order'] = self.order
        sort_order = self.get_ordering()
        if sort_order and sort_order[0] == '-':
            sort_order = sort_order[1:]
        context['sort_order'] = sort_order
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
