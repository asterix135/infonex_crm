from registration.models import *
from django.db.models import Count

def guess_company(company_name, postal_code, address1, city, name_first=False):

    company_best_guess = None
    company_suggest_list = []
    if name_first and postal_code in ('', None) and city in ('', None):
        print('option 0')
        match1 = Company.objects.filter(name__iexact=company_name)
    elif name_first and city not in ('', None):
        print('option 1')
        match1 = Company.objects.filter(name__iexact=company_name,
                                       city__iexact=city)
    else:
        print('option 2')
        match1 = Company.objects.filter(name__iexact=company_name,
                                        postal_code__iexact=postal_code)
    if match1.count() == 1:
        company_best_guess = match1[0]
        company_suggest_list.extend(list(match1))
    elif match1.count() > 1:
        ordered_list = match1.annotate(
            num_customers=Count('registrants')
        ).order_by('-num_customers')
        company_best_guess = ordered_list[0]
        company_suggest_list.extend(list(ordered_list))


    return company_best_guess, company_suggest_list
