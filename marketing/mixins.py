import csv
from django.http import HttpResponse
from django.utils.text import slugify
from django.views.generic import TemplateView


class DownloadResponseMixin():
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
            response['Content-Disposition'] = 'attachment; filename="%s.csv"' % slugify(context['title'])

            writer = csv.writer(response)
            # Write the data from the context somehow
            for item in context['items']:
                writer.writerow(item)

            return response
        # Business as usual otherwise
        else:
            return super(CSVResponseMixin, self).render_to_response(context, **response_kwargs)
