import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .filters import *
from .forms import *
from .models import *
from .constants import AC_DICT


#########################
#  Global Variables
#########################
TERRITORY_RECORDS_PER_PAGE = 50
TERRITORY_TAGS = [('geo', False),  # T/F indicates whether loose (text) match
                  ('main_category', False),
                  ('main_category2', False),
                  ('division1', False),
                  ('division2', False),
                  ('company', True),
                  ('industry', True)]


@login_required
def index(request):
    if 'event' in request.session:
        initial_event = Event.objects.get(pk=request.session['event'])
    else:
        initial_event = None
    territory_form = ListSelectForm(initial={'employee': request.user.pk,
                                             'event': initial_event})
    territory_form.fields['event'].queryset = Event.objects.filter(
        date_begins__gte=timezone.now()-datetime.timedelta(weeks=16)
    ).order_by('-date_begins', 'number')
    territory_form.fields['employee'].queryset = User.objects.filter(
        is_active=True
    )

    # check for permission to view all records
    user = request.user
    edit_permission_ok = (user.groups.filter(name='db_admin').exists() or
                          user.is_superuser)

    context = {
        'user_is_admin': edit_permission_ok,
        # 'land_filter': land_filter,
        'territory_form': territory_form,
    }
    return render(request, 'crm/index.html', context)


#################
# HELPER FUNCTION
#################
def update_person(request, person):
    # updated modified info before copying to change file
    person.modified_by = request.user
    person.date_modified = timezone.now()
    person.save()

    # write original record to change file
    add_change_record(person, 'update')

    # modify live record
    person.name = request.POST['name']
    person.title = request.POST['title']
    person.dept = request.POST['dept']
    person.company = request.POST['company']
    person.city = request.POST['city']
    person.phone = request.POST['phone']
    person.phone_main = request.POST['phone_main']
    person.email = request.POST['email']
    person.url = request.POST['url']
    person.do_not_call = request.POST.get('do_not_call', False)
    person.do_not_email = request.POST.get('do_not_email', False)
    person.industry = request.POST['industry']

    person.save()


#################
# HELPER FUNCTION
#################
def update_category_info(request, person):
    person.modified_by = request.user
    person.date_modified = timezone.now()
    person.save()

    # write original record to change file
    add_change_record(person, 'update')

    # modify live record
    # TODO: See if these should require permission level to modify
    person.dept = request.POST['dept']
    person.main_category = request.POST['main_category']
    person.division1 = request.POST['division1']
    person.division2 = request.POST['division2']
    person.geo = request.POST['geo']

    person.save()


@login_required
def detail(request, person_id):
    """
    View for detail.html
    """
    # Deal with deletion of recent contact
    if 'rm' in request.GET:
        if Contact.objects.filter(pk=request.GET.get('rm')).exists():
            contact = Contact.objects.get(pk=request.GET.get('rm'))
            if contact.able_to_delete():
                contact.delete()

    person = get_object_or_404(Person, pk=person_id)
    reg_history = person.reghistory_set.all()

    territory_boolean = territory_exists(request)
    if request.session.get('event') is not None:
        event = Event.objects.get(pk=request.session.get('event'))
    else:
        event = None
    if request.session.get('employee') is not None:
        salesperson = User.objects.get(pk=request.session.get('employee'))
    else:
        salesperson = None

    if request.method == 'POST' and request.POST['form'] == 'person':
        person_form = PersonUpdateForm(request.POST)
        if person_form.is_valid():
            update_person(request, person)
        contact_form = NewContactForm(initial={'event': event})
        category_form = PersonCategoryUpdateForm(instance=person)

    elif request.method == 'POST' and request.POST['form'] == 'category':
        category_form = PersonCategoryUpdateForm(request.POST)
        if category_form.is_valid():
            update_category_info(request, person)
        person_form = PersonUpdateForm(instance=person)
        contact_form = NewContactForm(initial={'event': event})

    elif request.method == 'POST' and request.POST['form'] == 'contact':
        contact_form = NewContactForm(request.POST)
        if contact_form.is_valid():
            add_contact(request, person)
        person_form = PersonUpdateForm(instance=person)
        category_form = PersonCategoryUpdateForm(instance=person)

    else:
        contact_form = NewContactForm(initial={'event': event})
        person_form = PersonUpdateForm(instance=person)
        category_form = PersonCategoryUpdateForm(instance=person)

    context = {
        'person': person,
        'person_form': person_form,
        'contact_form': contact_form,
        'territory_exists': territory_boolean,
        'event': event,
        'salesperson': salesperson,
        'category_form': category_form,
        'url_exists': len(person.url) > 0,
        'reg_history': reg_history,
    }
    return render(request, 'crm/detail.html', context)


@login_required
def add_person_to_territory(request, person_id):
    person = Person.objects.get(pk=person_id)
    event = Event.objects.get(pk=request.session.get('event'))
    employee = User.objects.get(pk=request.session.get('employee'))
    new_select = ListSelection(
        employee=employee,
        event=event,
        include_exclude='include',
        person=person,
    )
    new_select.save()
    return redirect(reverse('crm:detail', args=(person_id,)))


@login_required
def detail_paginated(request):
    """
    View to create dynamically referenced Person pages that can be
    gone through one by one
    :param request:
    :return:
    """
    # Deal with deletion of recent contact
    if 'rm' in request.GET:
        if Contact.objects.filter(pk=request.GET.get('rm')).exists():
            contact = Contact.objects.get(pk=request.GET.get('rm'))
            if contact.able_to_delete():
                contact.delete()

    # Pull relevant cookies
    employee = request.session.get('employee')
    territory_event = request.session.get('event')
    sort_col = request.session.get('sort_col')
    sort_order = request.session.get('sort_order')

    # If no sort order, set to reverse revision date order & set cookies
    if not sort_col:
        sort_col = 'date_modified'
        request.session['sort_col'] = sort_col
    if not sort_order:
        sort_order = 'DESC'
        request.session['sort_order'] = sort_order

    # If missing employee cookie, set to current user
    if not employee:
        employee = request.user.pk

    # If missing event, send back to index page
    if not territory_event:
        return HttpResponseRedirect(reverse('crm:index'))

    # Pull relevant records
    employee = User.objects.get(pk=employee)
    territory_event = Event.objects.get(pk=territory_event)
    territory = generate_territory_list(employee, territory_event,
                                        sort_col, sort_order)

    # if we get here with a ?pk= then determine the page number of the record
    if 'pk' in request.GET:
        active_person = Person.objects.get(pk=request.GET.get('pk'))
        for i in range(len(territory)):
            if active_person == territory[i]:
                request.session['detail_page'] = i + 1
                break

    paginator = Paginator(territory, 1)  # One contact per page

    if 'page' in request.GET:
        page = request.session['detail_page'] = request.GET['page']
    else:
        page = request.session.get('detail_page')
    try:
        person_list = paginator.page(page)
    except PageNotAnInteger:
        # if page not an integer, deliver first page
        person_list = paginator.page(1)
        page = 1
    except EmptyPage:
        # if page out of range, deliver last page of results
        person_list = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    person = paginator.page(page).object_list[0]

    if request.method == 'POST' and request.POST['form'] == 'person':
        person_form = PersonUpdateForm(request.POST)
        if person_form.is_valid():
            update_person(request, person)
        contact_form = NewContactForm(initial={'event': territory_event,})
        category_form = PersonCategoryUpdateForm(instance=person)

    elif request.method == 'POST' and request.POST['form'] == 'category':
        category_form = PersonCategoryUpdateForm(request.POST)
        if category_form.is_valid():
            update_category_info(request, person)
        person_form = PersonUpdateForm(instance=person)
        contact_form = NewContactForm(initial={'event': territory_event})

    elif request.method == 'POST' and request.POST['form'] == 'contact':
        contact_form = NewContactForm(request.POST)
        if contact_form.is_valid():
            add_contact(request, person)
        person_form = PersonUpdateForm(instance=person)
        category_form = PersonCategoryUpdateForm(instance=person)

    else:
        contact_form = NewContactForm(initial={'event': territory_event,})
        person_form = PersonUpdateForm(instance=person)
        category_form = PersonCategoryUpdateForm(instance=person)

    reg_history = person.reghistory_set.all()

    context = {'person_list': person_list,
               'person_form': person_form,
               'contact_form': contact_form,
               'person': person,
               'salesperson': employee,
               'active_event': territory_event,
               'flag_form': FlagForm(),
               'category_form': category_form,
               'reg_history': reg_history,
               'has_minus4': int(page) - 4 > 0,
               'has_minus3': int(page) - 3 > 0,
               'minus3': str(int(page) - 3),
               'has_minus2': int(page) - 2 > 0,
               'minus2': str(int(page) - 2),
               'has_minus1': int(page) - 1 > 0,
               'minus1': str(int(page) - 1),
               'has_plus1': int(page) + 1 <= paginator.num_pages,
               'plus1': str(int(page) + 1),
               'has_plus2': int(page) + 2 <= paginator.num_pages,
               'plus2': str(int(page) + 2),
               'has_plus3': int(page) + 3 <= paginator.num_pages,
               'plus3': str(int(page) + 3),
               'has_plus4': int(page) + 4 <= paginator.num_pages,
               'url_exists': len(person.url) > 0,
               }
    return render(request, 'crm/detail_paginated.html', context)


#################
# HELPER FUNCTION
#################
def add_change_record(person, change_action):
    """
    Called from updates/changes/deletes
    Records information in changes d/b for review and recovery
    Needs to be called before modification for
    :param person: Instance of Person Model pre-modification
    :param change_action: string indicating change (add/delete/update)
    """
    change = Changes(
        action=change_action,
        orig_id=person.pk,
        name=person.name,
        title=person.title,
        company=person.company,
        phone=person.phone,
        phone_main=person.phone_main,
        email=person.email,
        do_not_email=person.do_not_email,
        do_not_call=person.do_not_call,
        city=person.city,
        dept=person.dept,
        industry=person.industry,
        geo=person.geo,
        main_category=person.main_category,
        main_category2=person.main_category2,
        division1=person.division1,
        division2=person.division2,
        date_created=person.date_created,
        created_by=person.created_by,
        date_modified=timezone.now(),
        modified_by=person.created_by,
    )
    change.save()


#################
# HELPER FUNCTION
#################
def territory_exists(request):
    """
    Check if territory keys are defined for session and return boolean
    :param request:
    :return: boolean
    """
    if request.session.get('event') and request.session.get('employee'):
        return True
    else:
        return False


@login_required
def delete_person(request):
    """
    Refers to delete confirmation page and stores whether to return to
    paginated or absolute detail
    """
    person = get_object_or_404(Person, pk=request.GET.get('id'))
    request.session['ref'] = request.GET.get('ref')
    context = {'person': person, }
    return render(request, 'crm/delete_person.html', context)


@login_required
def confirm_delete(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    # copy contact data to DeletedConcact
    for contact in person.contact_set.all():
        del_contact = DeletedContact(
            original_pk=contact.pk,
            original_person_id=contact.author.pk,
            event=contact.event,
            date_of_contact=contact.date_of_contact,
            notes=contact.notes,
            method=contact.notes,
        )
        del_contact.save()
    # copy person record to Changes
    add_change_record(person, 'delete')
    # delete record (should cascade to Contact)
    person.delete()

    if request.session.get('ref') == 'absolute':
        # setup stuff for list page
        person_filter = PersonFilter(request.GET, queryset=Person.objects.all())
        context = {  # 'persons_all': persons_all,
               'person_filter': person_filter,
        }
        del request.session['ref']
        return render(request, "crm/list.html", context)
    else:
        del request.session['ref']
        return redirect(reverse('crm:territory'))


@login_required
def new_person(request):
    if request.method == 'POST':
        form = PersonUpdateForm(request.POST)
        if form.is_valid():
            person = Person(
                name=request.POST['name'],
                title=request.POST['title'],
                company=request.POST['company'],
                phone=request.POST['phone'],
                phone_main=request.POST['phone_main'],
                do_not_call=request.POST.get('do_not_call', False),
                email=request.POST['email'],
                do_not_email=request.POST.get('do_not_email', False),
                industry=request.POST['industry'],
                dept=request.POST['dept'],
                main_category=request.POST['main_category'],
                division1=request.POST['division1'],
                division2=request.POST['division2'],
                date_created=timezone.now(),
                date_modified=timezone.now(),
                created_by=request.user,
                modified_by=request.user,
            )
            person.save()

            # Add to current territory if checked and territory exists
            if 'include_in_territory' in request.POST:
                if territory_exists(request):
                    event = Event.objects.get(pk=request.session.get('event'))
                    employee = User.objects.get(
                        pk=request.session.get('employee'))
                    new_select = ListSelection(
                        employee=employee,
                        event=event,
                        include_exclude='include',
                        person=person,
                    )
                    new_select.save()

            add_change_record(person, 'new')
            print(request.GET.get('ref'))
            if request.GET.get('ref') == 'paginated':
                redirect_url = reverse('crm:detail_paginated')
                extra_params = '?pk=%s' % person.id
                full_redirect_url = '%s%s' % (redirect_url, extra_params)
                return HttpResponseRedirect(full_redirect_url)
            else:  # ref=absolute
                return HttpResponseRedirect(reverse('crm:detail',
                                                args=(person.id,)))
    form_status = request.GET.get('status')
    if form_status == 'copy':
        person_id = request.GET.get('id')
        person = get_object_or_404(Person, pk=person_id)
        form = PersonUpdateForm(instance=person)
    else:
        form = PersonUpdateForm()
    context = {
        'person_form': form,
        'territory_exists': territory_exists(request),
    }
    return render(request, 'crm/new_person.html', context)


#################
# HELPER FUNCTION
#################
def add_contact(request, person):
    event = get_object_or_404(Event, pk=request.POST['event'])

    new_contact = Contact(
        person=person,
        event=event,
        date_of_contact=timezone.now(),
        notes=request.POST['notes'],
        method=request.POST['method'],
        author=request.user
    )
    new_contact.save()

    # update person to show last contact
    person.date_modified = timezone.now()
    person.modified_by = request.user
    person.save()


@login_required
def person_list(request):
    # Bounce if permissions not correct
    if not (request.user.groups.filter(name='db_admin').exists() or
            request.user.is_superuser):
        return redirect(reverse('crm:index'))

    person_filter = PersonFilter(request.GET, queryset=Person.objects.all())

    paginator = Paginator(person_filter, TERRITORY_RECORDS_PER_PAGE)
    page = request.GET.get('page')
    try:
        page_person_list = paginator.page(page)
    except PageNotAnInteger:
        page_person_list = paginator.page(1)
        page = 1
    except EmptyPage:
        page_person_list = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    context = {  # 'persons_all': persons_all,
               'person_filter': person_filter,
               'page_person_list': page_person_list}
    return render(request, "crm/list.html", context)


#################
# HELPER FUNCTION
#################
def execute_person_search(name, title, company, state_province, past_customer,
                          sort_col, sort_order):
    """
    Helper function to filter records on search_person call
    returns sorted QuerySet
    """
    past_customer = past_customer == 'True' if past_customer is not None \
        else None
    search_list = Person.objects.all()
    if name:
        search_list = search_list.filter(name__icontains=name)
    if title:
        search_list = search_list.filter(title__icontains=title)
    if company:
        search_list = search_list.filter(company__icontains=company)
    if state_province:
        regex_val = r''
        for area_code in AC_DICT:
            if AC_DICT[area_code] == state_province:
                regex_val += '^' + area_code + '|^\(' + area_code + '|'
        regex_val = regex_val[:-1]
        search_list = search_list.filter(phone__regex=regex_val)
    if past_customer is not None:
        search_list = search_list.filter(reghistory__isnull=not past_customer)

    search_list = search_list.order_by(sort_col)
    if sort_order == 'DESC':
        search_list = search_list.reverse()
    return search_list


@login_required
def search_persons(request):
    # Set sort criteria
    if 'sort' not in request.GET:
        sort_col = request.session.get('sort_col')
    else:
        if request.GET['sort'] == request.session.get('sort_col'):
            request.session['sort_order'] = 'ASC' if \
                request.session['sort_order'] == 'DESC' else 'DESC'
        else:
            request.session['sort_order'] = 'ASC'
            request.session['sort_col'] = request.GET['sort']
        sort_col = request.session['sort_col']
    sort_order = request.session.get('sort_order')

    # If no sort order, set to ascending by company name & set cookies
    if not sort_col:
        sort_col = 'company'
        request.session['sort_col'] = sort_col
    if not sort_order:
        sort_order = 'ASC'
        request.session['sort_order'] = sort_order

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            # make sure search criteria exist
            if (request.POST['name']) or \
                    (request.POST['title']) or \
                    (request.POST['company']) or \
                    (request.POST['state_province']):
                # execute search
                if request.POST['name']:
                    request.session['search_name'] = name = request.POST['name']
                else:
                    request.session['search_name'] = name = None

                if request.POST['title']:
                    request.session['search_title'] = \
                        title = request.POST['title']
                else:
                    request.session['search_title'] = title = None

                if request.POST['company']:
                    request.session['search_company'] = company = \
                        request.POST['company']
                else:
                    request.session['search_company'] = company = None

                if request.POST['state_province']:
                    request.session['search_state'] = state_province = \
                        request.POST['state_province']
                else:
                    request.session['search_state'] = state_province = None

                if request.POST['past_customer']:
                    request.session['search_customer'] = past_customer = \
                        request.POST['past_customer']
                else:
                    request.session['search_customer'] = past_customer = None

                # sort results by sort criteria
                search_list = execute_person_search(
                    name, title, company, state_province, past_customer,
                    sort_col, sort_order
                )

            else:  # No search criteria = no names
                search_list = Person.objects.none()
        else:
            search_list = Person.objects.none()
    else:
        name = request.session['search_name'] if 'search_name' in \
            request.session else None
        title = request.session['search_title'] if 'search_title' in \
            request.session else None
        company = request.session['search_company'] if 'search_company' in \
            request.session else None
        state_province = request.session['search_state'] if 'search_state' in \
            request.session else None
        past_customer = request.session['search_customer'] if \
            'search_customer' in request.session else None

        form = SearchForm(initial={
            'name': name,
            'title': title,
            'company': company,
            'state_province': state_province,
            'past_customer': past_customer,
        })

        if name or title or company or state_province:
            search_list = execute_person_search(name,
                                                title,
                                                company,
                                                state_province,
                                                past_customer,
                                                sort_col,
                                                sort_order)
        else:
            search_list = Person.objects.none()

    paginator = Paginator(search_list, TERRITORY_RECORDS_PER_PAGE)

    if 'page' in request.GET:
        page = request.session['search_page'] = request.GET['page']
    else:
        page = request.session.get('search_page')

    try:
        person_list = paginator.page(page)
    except PageNotAnInteger:
        # if page not an integer, deliver first page
        person_list = paginator.page(1)
        page = 1
    except EmptyPage:
        # if page out of range, deliver last page of results
        person_list = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    context = {
        'search_form': form,
        'person_list': person_list,
        'has_minus4': int(page) - 4 > 0,
        'has_minus3': int(page) - 3 > 0,
        'minus3': str(int(page) - 3),
        'has_minus2': int(page) - 2 > 0,
        'minus2': str(int(page) - 2),
        'has_minus1': int(page) - 1 > 0,
        'minus1': str(int(page) - 1),
        'has_plus1': int(page) + 1 <= paginator.num_pages,
        'plus1': str(int(page) + 1),
        'has_plus2': int(page) + 2 <= paginator.num_pages,
        'plus2': str(int(page) + 2),
        'has_plus3': int(page) + 3 <= paginator.num_pages,
        'plus3': str(int(page) + 3),
        'has_plus4': int(page) + 4 <= paginator.num_pages,
    }
    return render(request, 'crm/search_persons.html', context=context)


######################
# Helper function for generate_territory_list
######################
def append_sql_criterion(select_criterion, param_list, current_select, started,
                         field_name, text_search=False):
    if not started:
        current_select = '('
        started = True
    else:
        current_select = current_select + ' AND '
    if text_search:
        current_select = current_select + 'p.' + field_name + \
            ' LIKE %s '
        param_list.append('%' + select_criterion + '%')
    else:
        current_select = current_select + 'p.' + field_name + ' = %s '
        param_list.append(select_criterion)
    return current_select, started


######################
# Helper function for territory_list and create_territory etc
######################
def generate_territory_list(employee, event, sort_col='date_modified',
                            sort_order='DESC', filter_active=False,
                            request=None):
    """
    Should generate an SQL statement something like:

    SELECT q.*
    FROM(
    SELECT p.id, p.name, p.company, p.geo, p.main_category, p.main_category2,
        p.division1, p.division2, p.industry, p.date_modified, p.title,
        f.id AS flag_id, f.flag AS flag_val, f.follow_up_date AS fup_date
    FROM crm_person as p
    LEFT JOIN (
        SELECT id, flag, person_id, follow_up_date
        FROM crm_personflag
        WHERE employee_id = 2
            AND event_id = 2) AS f
        ON f.person_id = p.id
    WHERE (
        ((p.main_category = 'Aboriginal' ))
        AND NOT ((p.company LIKE '%infonex%' ))
        OR p.id IN (4, 39, 19)
        ) AND (
            p.phone REGEXP '^573|^[(]573|^816|^[(]816|^557|^[(]557'
        )
    ) as z
    INNER JOIN crm_reghistory ON crm_reghistory.person_id = z.id
    ORDER BY q.company ASC;

    Args:
        employee:
        event:
        sort_col:
        sort_order:
        filter_active:
        request:

    Returns:

    """
    if request is None:
        request = {}
    # Get selection criteria for territory
    select_criteria = ListSelection.objects.filter(
        employee=employee
    ).filter(
        event=event
    )
    # If no select criteria, return empty Query set
    if len(select_criteria) == 0:
        return Person.objects.none()

    # Instantiate variables to hold stuff for final SQL
    include_selects = []
    include_params = []
    exclude_selects = []
    exclude_params = []
    has_person_includes = False
    person_includes = []
    has_person_excludes = False
    person_excludes = []
    has_customer_filter = False
    sql = "SELECT p.id, p.name, p.company, p.geo, p.main_category, " \
          "p.main_category2, p.division1, p.division2, p.industry, " \
          "p.date_modified, p.title, " \
          "f.id AS flag_id, f.flag AS flag_val, f.follow_up_date AS fup_date " \
          "FROM crm_person as p " \
          "LEFT JOIN (" \
          "SELECT id, flag, person_id, follow_up_date " \
          "FROM crm_personflag " \
          "WHERE employee_id = %s AND event_id = %s) AS f " \
          "ON f.person_id = p.id " \
          "WHERE "

    # start parenthesis around criteria if filtering territory
    if filter_active:
        sql += '('

    # build various parts of WHERE clause
    for criterion in select_criteria:
        if criterion.person:
            if criterion.include_exclude == 'include':
                has_person_includes = True
                person_includes.append(criterion.person_id)
            else:
                has_person_excludes = True
                person_excludes.append(criterion.person_id)
        elif criterion.include_exclude == 'include':
            started = False
            current_select = ''
            for tag in TERRITORY_TAGS:
                if getattr(criterion, tag[0]):
                    current_select, started = append_sql_criterion(
                        getattr(criterion, tag[0]), include_params,
                        current_select, started, tag[0], tag[1]
                    )
            include_selects.append(current_select + ')')
        else:  # This is an exclude
            started = False
            current_select = ''
            for tag in TERRITORY_TAGS:
                if getattr(criterion, tag[0]):
                    current_select, started = append_sql_criterion(
                        getattr(criterion, tag[0]), exclude_params,
                        current_select, started, tag[0], tag[1]
                    )
            exclude_selects.append(current_select + ')')

    final_sql_params = [employee.pk, event.pk]
    started = False

    if len(include_selects) > 0:
        started = True
        sql = sql + '('
        for i in range(len(include_selects)):
            sql = sql + include_selects[i] + ' OR '
        sql = sql[:-4] + ') '
        final_sql_params.extend(include_params)

    if len(exclude_selects) > 0:
        if started:
            sql = sql + 'AND '
        started = True
        sql = sql + 'NOT ('
        for i in range(len(exclude_selects)):
            sql = sql + exclude_selects[i] + ' AND '
        sql = sql[:-5] + ') '
        final_sql_params.extend(exclude_params)

    if has_person_includes:
        if started:
            sql = sql + 'OR '
        started = True
        sql = sql + 'p.id IN (' + '%s, ' * len(person_includes)
        sql = sql[:-2]  + ') '
        final_sql_params.extend(person_includes)

    if has_person_excludes:
        if started:
            sql = sql + 'AND '
        started = True
        sql = sql + 'NOT p.id IN (' + '%s, ' * len(person_excludes)
        sql = sql[:-2] +') '
        final_sql_params.extend(person_excludes)

    # If everything was blank, return empty query set
    if not started:
        return Person.objects.none()

    # If territory is filtered, add filter clause to WHERE clause
    if filter_active:
        filter_clause_started=False
        filter_params = []
        sql += ') AND ('
        if 'filter_name' in request.session and \
                request.session['filter_name'] is not None:
            filter_clause_started = True
            sql += 'p.name LIKE %s '
            filter_params.append('%' + request.session['filter_name'] + '%')
        if 'filter_title' in request.session and \
                request.session['filter_title'] is not None:
            if filter_clause_started:
                sql += 'AND '
            else:
                filter_clause_started = True
            sql += 'p.title LIKE %s '
            filter_params.append('%' + request.session['filter_title'] + '%')
        if 'filter_company' in request.session and \
                request.session['filter_company'] is not None:
            if filter_clause_started:
                sql += 'AND '
            else:
                filter_clause_started = True
            sql += 'p.company LIKE %s '
            filter_params.append('%' + request.session['filter_company'] + '%')
        if 'filter_flag' in request.session and \
                request.session['filter_flag'] is not None:
            if filter_clause_started:
                sql += 'AND '
            else:
                filter_clause_started = True
            sql += 'f.flag = %s '
            filter_params.append(request.session['filter_flag'])

        # have to search state by area code
        if 'filter_state' in request.session and \
                request.session['filter_state'] is not None:
            if filter_clause_started:
                sql += 'AND '
            else:
                filter_clause_started = True
            sql += 'p.phone REGEXP "'
            ac_list = []
            for area_code in AC_DICT:
                if AC_DICT[area_code] == request.session['filter_state']:
                    sql += '^' + area_code + '|^[(]' + area_code + '|'
            sql = sql[:-1] + '" '

        # flag whether we have to deal with setting up an outer join
        if 'filter_customer' in request.session and \
                request.session['filter_customer'] is not None:
            has_customer_filter = True
            sql = 'SELECT q.* FROM (' + sql
            if filter_clause_started:
                sql += ')'
            else:
                sql = sql[:-5]
            sql += ') AS q ' \
                   'INNER JOIN crm_reghistory ' \
                   'ON crm_reghistory.person_id = q.id '

        if not has_customer_filter:
            sql += ') '
        final_sql_params.extend(filter_params)

    # Add in ordering to sql
    if has_customer_filter:
        prefix = 'q'
    elif sort_col == ('flag' or 'fup_date'):
        prefix = 'f'
    else:
        prefix = 'p'

    sql = sql + 'ORDER BY ' + prefix + '.' + sort_col + ' ' + sort_order

    territory = Person.objects.raw(sql, final_sql_params)
    return list(territory)


@login_required
def set_territory_params(request):
    """
    Called when setting session territory values to something new
    eg: index page, or sidebar
    :param request:
    :return:
    """
    if request.method == 'POST':
        if 'event' in request.POST:
            request.session['event'] = request.POST['event']
        if 'employee' in request.POST:
            request.session['employee'] = request.POST['employee']

        user = request.user
        edit_permission_ok = (user.groups.filter(name='db_admin').exists() or
                              user.is_superuser)
        if 'submit_option' in request.POST and \
                request.POST['submit_option'] == 'edit_territory' and \
                edit_permission_ok:
            # return create_territory(request)
            return HttpResponseRedirect('/crm/create_territory/')
    # return territory_list(request)
    return HttpResponseRedirect('/crm/territory/')


@login_required
def territory_list(request):
    """
    Provides selected territory list for user & event
    """

    # Pull relevant cookies
    employee = request.session.get('employee')
    territory_event = request.session.get('event')
    if 'sort' not in request.GET:
        sort_col = request.session.get('sort_col')
    else:
        if request.GET['sort'] == request.session.get('sort_col'):
            request.session['sort_order'] = 'ASC' if \
                request.session['sort_order'] == 'DESC' else 'DESC'
        else:
            request.session['sort_order'] = 'ASC'
            request.session['sort_col'] = request.GET['sort']
        sort_col = request.session['sort_col']
    sort_order = request.session.get('sort_order')

    # If no sort order, set to ascending by company name & set cookies
    if not sort_col:
        sort_col = 'company'
        request.session['sort_col'] = sort_col
    if not sort_order:
        sort_order = 'ASC'
        request.session['sort_order'] = sort_order

    # Missing employee cookie -> set to current user
    if not employee:
        request.session['employee'] = request.user.pk
        employee = request.user.pk

    if not territory_event:
        # take user back to index page
        return HttpResponseRedirect(reverse('crm:index'))
        # territory = Person.objects.all()
        # employee = User.get(pk=1)
        # territory_event = Event.get(pk=1)

    # Set cookies for filter values
    if request.method == 'POST':
        if request.POST['option'] == 'filter':
            request.session['filter_name'] = request.POST['name'] if \
                len(request.POST['name']) > 0 else None
            request.session['filter_title'] = request.POST['title'] if \
                len(request.POST['title']) > 0 else None
            request.session['filter_company'] = request.POST['company'] if \
                len(request.POST['company']) > 0 else None
            request.session['filter_state'] = request.POST['state_province'] \
                if len(request.POST['state_province']) > 0 else None
            request.session['filter_flag'] = request.POST['flag'] if \
                len(request.POST['flag']) > 0 else None
            request.session['filter_customer'] = 'True' if \
                ('past_customer' in request.POST) else None
        else:
            request.session['filter_name'] = None
            request.session['filter_title'] = None
            request.session['filter_company'] = None
            request.session['filter_state'] = None
            request.session['filter_flag'] = None
            request.session['filter_customer'] = None

    # Cookies exist - pull relevant records
    filter_active = any([
        'filter_name' in request.session and
            request.session['filter_name'] is not None,
        'filter_title' in request.session and
            request.session['filter_title'] is not None,
        'filter_company' in request.session and
            request.session['filter_company'] is not None,
        'filter_state' in request.session and
            request.session['filter_state'] is not None,
        'filter_flag' in request.session and
            request.session['filter_flag'] is not None,
        'filter_customer' in request.session and
            request.session['filter_customer'] is not None
    ])

    employee = User.objects.get(pk=employee)
    territory_event = Event.objects.get(pk=territory_event)
    territory = generate_territory_list(employee, territory_event, sort_col,
                                        sort_order, filter_active, request)

    paginator = Paginator(territory, TERRITORY_RECORDS_PER_PAGE)

    if 'page' in request.GET:
        page = request.session['territory_page'] = request.GET['page']
    else:
        page = request.session.get('territory_page')

    try:
        person_list = paginator.page(page)
    except PageNotAnInteger:
        # if page not an integer, deliver first page
        person_list = paginator.page(1)
        page = 1
    except EmptyPage:
        # if page out of range, deliver last page of results
        person_list = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    # Flag form
    flag_form = FlagForm()

    filter_form_vals = {
        'name': request.session['filter_name'] if
            ('filter_name' in request.session) else None,
        'title': request.session['filter_title'] if
            ('filter_title' in request.session) else None,
        'company': request.session['filter_company'] if
            ('filter_company' in request.session) else None,
        'past_customer': bool(request.session['filter_customer']) if
            ('filter_customer' in request.session) else None,
        'state_province': request.session['filter_state'] if
            ('filter_state' in request.session) else None,
        'flag': request.session['filter_flag'] if
            ('filter_flag' in request.session) else None,
    }
    filter_form = TerritorySearchForm(filter_form_vals)

    context = {'person_list': person_list,
               'employee': employee,
               'event': territory_event,
               'flag_form': flag_form,
               'filter_form': filter_form,
               'has_minus4': int(page) - 4 > 0,
               'has_minus3': int(page) - 3 > 0,
               'minus3': str(int(page) - 3),
               'has_minus2': int(page) - 2 > 0,
               'minus2': str(int(page) - 2),
               'has_minus1': int(page) - 1 > 0,
               'minus1': str(int(page) - 1),
               'has_plus1': int(page) + 1 <= paginator.num_pages,
               'plus1': str(int(page) + 1),
               'has_plus2': int(page) + 2 <= paginator.num_pages,
               'plus2': str(int(page) + 2),
               'has_plus3': int(page) + 3 <= paginator.num_pages,
               'plus3': str(int(page) + 3),
               'has_plus4': int(page) + 4 <= paginator.num_pages,
               }
    return render(request, 'crm/territory.html', context)


# TODO: probably should require permission level - how to do that??
@login_required
def create_territory(request):
    """
    Used to create a territory for a salesperson
    """
    employee = User.objects.get(pk=request.session.get('employee'))
    territory_event = Event.objects.get(pk=request.session.get('event'))
    select_form = ListSelectForm

    # if we get here from territory_list
    if request.method == 'POST' and \
            request.POST['submit_option'].lower() == 'save':
        # create new list select
        new_select = ListSelection(
            employee=employee,
            event=territory_event,
            geo=request.POST['geo'],
            main_category=request.POST['main_category'],
            main_category2=request.POST['main_category2'],
            division1=request.POST['division1'],
            division2=request.POST['division2'],
            company=request.POST['company'],
            industry=request.POST['industry'],
            include_exclude=request.POST['include_exclude'],
        )
        new_select.save()
    elif request.method == 'POST' and \
            request.POST['submit_option'].lower() == 'delete':
        list_select = ListSelection.objects.get(pk=request.POST['select_id'])
        list_select.delete()

    select_criteria = ListSelection.objects.filter(
        employee=employee
    ).filter(
        event=territory_event
    )
    # TODO: Consider making this sorting dynamic
    territory = generate_territory_list(employee, territory_event,
                                        'company', 'ASC')

    # Set up pagination
    paginator = Paginator(territory, TERRITORY_RECORDS_PER_PAGE)
    page = request.GET.get('page')
    try:
        person_list = paginator.page(page)
    except PageNotAnInteger:
        # if page not an integer, deliver first page
        person_list = paginator.page(1)
        page = 1
    except EmptyPage:
        # if page out of range, deliver last page of results
        person_list = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    context = {
        'select_form': select_form,
        'employee': employee,
        'event': territory_event,
        'list_selects': select_criteria,
        'person_list': person_list,
        'has_minus4': int(page) - 4 > 0,
        'has_minus3': int(page) - 3 > 0,
        'minus3': str(int(page) - 3),
        'has_minus2': int(page) - 2 > 0,
        'minus2': str(int(page) - 2),
        'has_minus1': int(page) - 1 > 0,
        'minus1': str(int(page) - 1),
        'has_plus1': int(page) + 1 <= paginator.num_pages,
        'plus1': str(int(page) + 1),
        'has_plus2': int(page) + 2 <= paginator.num_pages,
        'plus2': str(int(page) + 2),
        'has_plus3': int(page) + 3 <= paginator.num_pages,
        'plus3': str(int(page) + 3),
        'has_plus4': int(page) + 4 <= paginator.num_pages,
    }
    return render(request, 'crm/create_territory.html', context)


@login_required
def flag_record(request):
    """
    Add flag and/or follow-up date for a Person for a salesperson & event
    """
    # store pagination data for later use
    if 'page' in request.POST and request.POST['page_source'] == 'territory':
        request.session['territory_page'] = request.POST['page']

    person = Person.objects.get(pk=request.POST['person_id'])
    event = Event.objects.get(pk=request.session.get('event'))
    employee = User.objects.get(pk=request.session.get('employee'))
    # if flag exists, we want to modify it, else create it
    if PersonFlag.objects.filter(
        person=person,
        event=event,
        employee=employee,
    ).exists():
        flag = PersonFlag.objects.get(
            person=person,
            event=event,
            employee=employee,
        )
    else:
        flag = PersonFlag(
            person=person,
            event=event,
            employee=employee,
        )
    flag.flag = request.POST['flag']

    if 'follow_up_date' in request.POST:
        flag.follow_up_date = request.POST['follow_up_date']
    flag.save()

    if request.POST['page_source'] == 'detail':
        redirect_url = reverse('crm:detail_paginated')
        extra_params = '?pk=%s' % person.id
        full_redirect_url = '%s%s' % (redirect_url, extra_params)
        return HttpResponseRedirect(full_redirect_url)
    else:
        return HttpResponseRedirect(reverse('crm:territory'))
