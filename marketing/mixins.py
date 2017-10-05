import csv
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.generic.detail import SingleObjectMixin


class IndexCSVResponseMixin():
    """
    A generic mixin that constructs a CSV response from the context data if
    the CSV export option was provided in the request.
    """
    def render_to_response(self, context, **response_kwargs):
        """
        Creates a CSV response if requested, otherwise returns the default
        template response.
        """
        # Sniff if we need to return a CSV export
        if 'csv' in self.request.GET.get('export', ''):
            response = HttpResponse(content_type='text/csv')
            export_file_name = 'database_download_' + \
                timezone.now().strftime('%Y-%b-%d') + '.csv'
            response['Content-Disposition'] = 'attachment; filename=' + \
                export_file_name

            writer = csv.writer(response)
            writer.writerow([
                'Name',
                'Title',
                'Company',
                'Phone',
                'PhoneAlternate',
                'PhoneMain',
                'DoNotCall',
                'Email',
                'EmailAlternate',
                'DoNotEmail',
                'URL',
                'LinkedIn',
                'City',
                'Dept',
                'Industry',
                'Geo',
                'MainCategory',
                'MainCategory2',
                'Division1',
                'Division2',
                'StateProv',
                'HasRegistrationHistory',
                'CreatedBy',
            ])
            for person in self.filtered_queryset:
                writer.writerow([
                    person.name,
                    person.title,
                    person.company,
                    person.phone,
                    person.phone_alternate,
                    person.phone_main,
                    person.do_not_call,
                    person.email,
                    person.email_alternate,
                    person.do_not_email,
                    person.url,
                    person.linkedin,
                    person.city,
                    person.dept,
                    person.industry,
                    person.geo,
                    person.main_category,
                    person.main_category2,
                    person.division1,
                    person.division2,
                    person.state_prov,
                    person.has_registration_history,
                    person.created_by.username,
                ])
            return response
        # Business as usual otherwise
        else:
            return super(IndexCSVResponseMixin, self).render_to_response(
                context, **response_kwargs
            )


class GeneratePaginationList():
    """
    Generates page numbers for lengthy paginations
    """

    def generate_pagination_list(self, context):
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

    def paginate_queryset(self, queryset, page_size):
        """
        Overrides ListView method to redirect to first or last page
        rather than throwing an 404 error
        """
        paginator = self.get_paginator(
            queryset, page_size, orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty())
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) \
               or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                page_number = 1
        try:
            page = paginator.page(page_number)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        return (paginator, page, page.object_list, page.has_other_pages())


class JsonResponseMixin():

    def get_json_data(self, **kwargs):
        return {}

    def render_to_response(self, context=None, **response_kwargs):
        return JsonResponse(self.get_json_data(**response_kwargs))


class MarketingPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.groups.filter(name='marketing').exists():
            return True
        if self.request.user.groups.filter(name='db_admin').exists():
            return True
        if self.request.user.groups.filter(name='management').exists():
            return True
        if self.request.user.is_superuser:
            return True
        return False
