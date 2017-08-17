import csv
from django.http import HttpResponse
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic import TemplateView


class CSVResponseMixin():
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
            n=0
            for person in self.filtered_queryset:
                print(n)
                n+=1
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
            return super(CSVResponseMixin, self).render_to_response(context, **response_kwargs)
