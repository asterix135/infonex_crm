from .constants import STOPWORDS, SEARCH_SUBSTITUTIONS
from registration.models import *
from django.db.models import Count, Q
import re

def iteratively_replace_and_guess_name(company_name):
    alternate_names = []
    name_with_all_replacements1 = company_name
    name_with_all_replacements2 = company_name
    for substitution in SEARCH_SUBSTITUTIONS:
        regex1 = re.compile(r'\b' + substitution[0].lower() + r'\b')
        regex2 = re.compile(r'\b' + substitution[1].lower() + r'\b')
        if regex1.search(company_name):
            alternate_names.append(regex1.sub(substitution[1], company_name))
            name_with_all_replacements1 = regex1.sub(substitution[1],
                                                     name_with_all_replacements1)
        if regex2.search(company_name):
            alternate_names.append(regex2.sub(substitution[0], company_name))
            name_with_all_replacements2 = regex2.sub(substitution[0],
                                                    name_with_all_replacements2)
    if name_with_all_replacements1 != company_name:
        alternate_names.append(name_with_all_replacements1)
    if name_with_all_replacements2 != company_name:
        alternate_names.append(name_with_all_replacements2)

    queries = []
    for name in alternate_names:
        if len(name) > 2:
            queries.append(Q(name__icontains=name))
        else:
            queries.append(Q(name__iexact=name))
    if len(queries) > 0:
        query = queries.pop()
        for item in queries:
            query |= item
        return Company.objects.filter(query)
    return Company.objects.none()


def order_list_by_registrants(queryset):
    return queryset.annotate(
        num_customers=Count('registrants')
    ).order_by('-num_customers')


def guess_company(company_name, postal_code, address1, city, name_first=False):
    company_name = ' '.join(company_name.lower().strip().split())
    company_best_guess = None
    company_suggest_list = []
    if name_first and postal_code in ('', None) and city in ('', None):
        match1 = Company.objects.filter(name__iexact=company_name)
    elif name_first and city not in ('', None):
        match1 = Company.objects.filter(name__iexact=company_name,
                                       city__iexact=city)
    else:
        match1 = Company.objects.filter(name__iexact=company_name,
                                        postal_code__iexact=postal_code)
    if match1.count() > 0:
        ordered_list = order_list_by_registrants(match1)
        company_best_guess = ordered_list[0]
        company_suggest_list.extend(list(ordered_list))

    match2 = iteratively_replace_and_guess_name(company_name)
    if name_first and city not in ('', None):
        match2 = match2.filter(city__icontains=city)
    elif (postal_code not in ('', None) or not name_first):
        match2 = match2.filter(postal_code__iexact=postal_code)
    if match2.count() > 0:
        ordered_list = order_list_by_registrants(match2)
        if not company_best_guess:
            company_best_guess = ordered_list[0]
        company_suggest_list.extend(list(ordered_list))

    # following searches are too iffy to set company_best_guess
    # check for companies containing text name as is
    match3 = Company.objects.filter(name__icontains=company_name)
    if match3.count() > 0:
        match3 = match3.exclude(id__in=match1).exclude(id__in=match2)
        ordered_list = order_list_by_registrants(match3)
        company_suggest_list.extend(list(ordered_list))

    # set up stuff
    if name_first and postal_code in ('', None):
        match_base = Company.objects.all()
    else:
        match_base = Company.objects.filter(postal_code=postal_code)
    match4 = Company.objects.none()
    match5 = Company.objects.none()

    # first try trigrams
    if len(company_name.split()) > 3 and len(company_suggest_list) < 15:
        queries = []
        trigram_list = zip(company_name.split(),
                           company_name.split()[1:],
                           company_name.split()[2:])
        for trigram in trigram_list:
            if trigram[0] not in STOPWORDS or trigram[1] not in STOPWORDS \
                or trigram[2] not in STOPWORDS:
                search_term = ' '.join(trigram)
                queries.append(Q(name__icontains=search_term))
        if len(queries) > 0:
            query = queries.pop()
            for item in queries:
                query |= item
            match4 = match_base.filter(query)
            match4 = match4.exclude(id__in=match1).exclude(id__in=match2). \
                exclude(id__in=match3)
            ordered_list = order_list_by_registrants(match4)
            company_suggest_list.extend(list(
                ordered_list[:15-len(company_suggest_list)]
            ))

    # next try bigrams
    if len(company_name.split()) > 2 and len(company_suggest_list) < 15:
        queries = []
        bigram_list = zip(company_name.split(),
                          company_name.split()[1:])
        for bigram in bigram_list:
            if bigram[0] not in STOPWORDS or bigram[1] not in STOPWORDS:
                search_term = ' '.join(bigram)
                queries.append(Q(name__icontains=search_term))
        if len(queries) > 0:
            query = queries.pop()
            for item in queries:
                query |= item
            match5 = match_base.filter(query)
            match5 = match5.exclude(id__in=match1).exclude(id__in=match2). \
                exclude(id__in=match3).exclude(id__in=match4)
            ordered_list = order_list_by_registrants(match5)
            company_suggest_list.extend(list(
                ordered_list[:15-len(company_suggest_list)]
            ))

    # finally try keywords
    if len(company_suggest_list) < 15:
        queries = []
        name_tokens = [x for x in company_name.split() if x not in STOPWORDS]
        for token in name_tokens:
            queries.append(Q(name__icontains=token))
        if len(queries) > 0:
            query = queries.pop()
            for item in queries:
                query |= item
            match6 = match_base.filter(query)
            match6 = match6.exclude(id__in=match1).exclude(id__in=match2). \
                exclude(id__in=match3).exclude(id__in=match4). \
                exclude(id__in=match5)
            ordered_list = order_list_by_registrants(match6)
            company_suggest_list.extend(list(
                ordered_list[:15-len(company_suggest_list)]
            ))

    return company_best_guess, company_suggest_list
