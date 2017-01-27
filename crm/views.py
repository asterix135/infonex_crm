import datetime
import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.views import View

from .forms import *
from .models import *
from .constants import *
from registration.forms import ConferenceSelectForm, ConferenceEditForm


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
def update_category_info_old(request, person):
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
def detail_old(request, person_id):
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
            update_category_info_old(request, person)
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
    return render(request, 'crm/detail_old.html', context)


@login_required
def add_person_to_territory_old(request, person_id):
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
            update_category_info_old(request, person)
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


# Can delete thi
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


# Can delete this
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
        del request.session['ref']
        return redirect(reverse('crm:search_persons'))
    else:
        del request.session['ref']
        return redirect(reverse('crm:territory'))


# Need to remove
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
                main_category2=request.POST['main_category'],
                geo=request.POST['geo'],
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
    return render(request, 'crm/territory_old.html', context)


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



##################
# NEW/OVERHAULED STUFF GOES BELOW HERE
##################

##################
# HELPER FUNCTIONS
##################

def add_change_record(person, change_action):
    """
    Called from updates/changes/deletes
    Records information in changes d/b for review and recovery
    Needs to be called before modification
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


def add_to_recent_contacts(request, person_id):
    """
    adds person to a user's recent contact list
    requires that person_id be validated before calling function
    """
    if 'recent_contacts' not in request.session:
        recent_contact_list = []
    else:
        recent_contact_list = request.session['recent_contacts']
    if person_id not in recent_contact_list:
        recent_contact_list.insert(0, person_id)
        recent_contact_list = recent_contact_list[:10]
    else:
        recent_contact_list.remove(person_id)
        recent_contact_list.insert(0, person_id)
    request.session['recent_contacts'] = recent_contact_list


def filter_personal_territory(request, territory_query_set, search_form=None):
    filter_options = (('name', 'filter_name', 'name__icontains'),
                      ('title', 'filter_title', 'title__icontains'),
                      ('company', 'filter_company', 'company__icontains'),
                      ('state_province', 'filter_prov'),
                      ('past_customer', 'filter_customer'))  # flag not in form
    if request.method == 'POST' and search_form and search_form.is_valid():
        for option in filter_options:
            if search_form.cleaned_data[option[0]] not in ('', None):
                request.session[option[1]] = search_form.cleaned_data[option[0]]
            elif option[1] in request.session:
                del request.session[option[1]]
            if 'flag' in request.POST and request.POST['flag'] != 'any':
                request.session['filter_flag'] = request.POST['flag']
            elif 'filter_flag' in request.session:
                del request.session['filter_flag']
    kwargs = {}
    for option in filter_options[:3]:  # customer, flag, reg are special cases
        if option[1] in request.session:
            kwargs[option[2]] = request.session[option[1]]
    territory_query_set = territory_query_set.filter(**kwargs)

    # deal with state filter
    if 'filter_prov' in request.session and \
        request.session['filter_prov'] != '':
        ac_tuple = AC_LOOKUP[request.session['filter_prov']]
        queries = []
        for ac in ac_tuple:
            re_term = r'^\s*\(?' + ac
            queries.append(Q(phone__iregex=re_term))
        query = queries.pop()
        for item in queries:
            query |= item
        territory_query_set = territory_query_set.filter(query)

    # deal with customer filter
    if 'filter_customer' in request.session:
        if request.session['filter_customer'] == 'True':
            territory_query_set = territory_query_set.filter(
                registrants__isnull=False
            ).distinct()
        elif request.session['filter_customer'] == 'False':
            territory_query_set = territory_query_set.filter(
                registrants__isnull=True
            )

    # deal with flag filter
    if 'filter_flag' in request.session and 'assignment_id' in request.session:
        event_assignment = EventAssignment.objects.get(
            pk=request.session['assignment_id']
        )
        if request.session['filter_flag'] not in ('none', 'any'):
            territory_query_set = territory_query_set.filter(
                flags__event_assignment=event_assignment,
                flags__flag=FLAG_COLORS[request.session['filter_flag']]
            )
        elif request.session['filter_flag'] == 'none':
            territory_query_set = territory_query_set.exclude(
                flags__event_assignment=event_assignment
            )

    return territory_query_set


def process_flag_change(request, person, event_assignment):
    try:
        flag = Flags.objects.get(person=person,
                                 event_assignment=event_assignment)
    except Flags.DoesNotExist:
        flag = Flags(person = person,
                     event_assignment = event_assignment)
    if request.POST['flag_color'] != 'none':
        flag.flag = FLAG_COLORS[request.POST['flag_color']]
        if 'followup' in request.POST:
            flag.follow_up_date = request.POST['followup']
        flag.save()
    else:
        if flag.id:
            flag.delete()
        flag = None
    return flag


def get_my_territories(user):
    """
    returns queryset of active EventAssignments for a user
    """
    my_assignments = EventAssignment.objects.filter(
        user=user,
        event__date_begins__gte=timezone.now()-datetime.timedelta(weeks=4)
    ).exclude(role='NA')
    return my_assignments


def build_master_territory_list(list_select_queryset):
    """
    Builds and returns query set based on a territory's master selection
    criteria
    """
    field_dict = {'main_category': 'main_category',
                  'main_category2': 'main_category2',
                  'geo': 'geo',
                  'industry': 'industry__icontains',
                  'company': 'company__icontains',
                  'dept': 'dept__icontains'}
    num_conditions = list_select_queryset.count()
    if num_conditions == 0:
        return Person.objects.none()
    territory_list = Person.objects.none()
    exclude_selects = []
    # First, build list by UNIONing includes
    includes_added = False
    for list_select in list_select_queryset:
        kwargs = {}
        for field in field_dict:
            if getattr(list_select, field) not in ['', None]:
                kwargs[field_dict[field]] = getattr(list_select, field)
        if list_select.include_exclude == 'include':
            includes_added = True
            query_list = Person.objects.filter(**kwargs)
            territory_list = territory_list | query_list
        else:
            exclude_selects.append(list_select)
    if len(exclude_selects) == 0:
        return territory_list
    if not includes_added:
        territory_list = Person.objects.all()
    for list_select in exclude_selects:
        kwargs = {}
        for field in field_dict:
            if getattr(list_select, field) not in ['', None]:
                kwargs[field_dict[field]] = getattr(list_select, field)
        territory_list = territory_list.exclude(**kwargs)
    return territory_list


def build_user_territory_list(event_assignment_object, for_staff_member=False):
    """
    param event_assignment_object: one Event Assignment Records
    param for_staff_member: boolean indicating whether list is for use on a
                            staff member's territory page (True)
    """
    field_dict = {'main_category': 'main_category',
                  'main_category2': 'main_category2',
                  'division1': 'division1',
                  'division2': 'division2',
                  'geo': 'geo',
                  'industry': 'industry__icontains',
                  'company': 'company__icontains',
                  'dept': 'dept__icontains'}
    if for_staff_member:
        field_dict['person'] = 'person_id'
    filter_main = event_assignment_object.filter_master_selects
    user_select_set = PersonalListSelections.objects.filter(
        event_assignment=event_assignment_object
    )
    if filter_main:
        event = event_assignment_object.event
        master_list_selects = MasterListSelections.objects.filter(
            event=event
        )
        territory_list = build_master_territory_list(master_list_selects)
        includes_added = True
        num_user_selects = user_select_set.count()
    else:
        territory_list = Person.objects.none()
        includes_added = False
        num_user_selects = user_select_set.exclude(include_exclude='filter').count()
    if num_user_selects == 0:
        return territory_list
    filter_selects=[]
    exclude_selects=[]
    for list_select in user_select_set:
        kwargs = {}
        if list_select.include_exclude == 'add':
            for field in field_dict:
                if getattr(list_select, field) not in ['', None]:
                    kwargs[field_dict[field]] = getattr(list_select, field)
            includes_added = True
            query_list = Person.objects.filter(**kwargs)
            territory_list = territory_list | query_list
        elif list_select.include_exclude == 'filter':
            filter_selects.append(list_select)
        else:
            exclude_selects.append(list_select)
    if len(filter_selects) + len(exclude_selects) == 0:
        return territory_list

    # Process each filter separately and then OR them together
    if len(filter_selects) > 0 and filter_main:
        filtered_querysets = []
        for list_select in filter_selects:
            kwargs = {}
            for field in field_dict:
                if getattr(list_select, field) not in ['', None]:
                    kwargs[field_dict[field]] = getattr(list_select, field)
            filtered_querysets.append(territory_list.filter(**kwargs))
        territory_list = filtered_querysets.pop()
        while len(filtered_querysets) > 0:
            territory_list |= filtered_querysets.pop()
        if len(exclude_selects) == 0:
            return territory_list

    # Process excludes
    if not includes_added:
        territory_list = Person.objects.all()
    for list_select in exclude_selects:
        kwargs = {}
        for field in field_dict:
            if getattr(list_select, field) not in ['', None]:
                kwargs[field_dict[field]] = getattr(list_select, field)
        territory_list = territory_list.exclude(**kwargs)
    return territory_list


def has_management_permission(user):
    """
    To be called by textdecorator @user_passes_test
    Also, any time you need to check if user has management permissions
    """
    if user.groups.filter(name='db_admin').exists():
        return True
    if user.groups.filter(name='management').exists():
        return True
    if user.is_superuser:
        return True
    return False


##################
# MAIN FUNCTIONS
##################

@login_required
def delete(request):
    if request.method != 'POST':
        return HttpResponseRedirect('/crm/search/')
    try:
        person = Person.objects.get(pk=request.POST['person_id'])
    except (Person.DoesNotExist, MultiValueDictKeyError):
        raise Http404('Person has already been deleted')

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
    add_change_record(person, 'delete')
    person.delete()
    return HttpResponseRedirect('/crm/search/')


@login_required
def detail(request, person_id):
    """ loads main person page (detail.html) """
    new_contact_form = NewContactForm()
    reg_list = None
    flag = None
    in_territory = False
    event_assignment = None
    try:
        person = Person.objects.get(pk=person_id)
        add_to_recent_contacts(request, person_id)
        if person.registrants_set.exists():
            for registrant in person.registrants_set.all():
                # reg_list = registrant.regdetails_set.all()
                if not reg_list:
                    reg_list = registrant.regdetails_set.all()
                else:
                    reg_list = reg_list | registrant.regdetails.set.all()
            if reg_list.count() == 0:
                reg_list = None
            else:
                reg_list = reg_list.order_by('-register_date')
    except (Person.DoesNotExist, MultiValueDictKeyError):
        raise Http404('Person is not in the Database')
    person_details_form = PersonDetailsForm(instance=person)
    category_form = PersonCategoryUpdateForm(instance=person)

    # Check if person is part of current territory - if so fetch flag details
    if 'assignment_id' in request.session:
        try:
            event_assignment = EventAssignment.objects.get(
                pk=request.session['assignment_id']
            )
            my_territory = build_user_territory_list(event_assignment, True)
            if my_territory.filter(id=person.id).exists():
                in_territory = True
                try:
                    flag = Flags.objects.get(person=person,
                                             event_assignment=event_assignment)
                except Flags.DoesNotExist:
                    pass  # default variable settings are fine
        except EventAssignment.DoesNotExist:
            pass  # default variable settings are fine

    context = {
        'flag': flag,
        'in_territory': in_territory,
        'event_assignment': event_assignment,
        'my_territories': get_my_territories(request.user),
        'person': person,
        'person_details_form': person_details_form,
        'new_contact_form': new_contact_form,
        'category_form': category_form,
        'reg_list': reg_list,
    }
    return render(request, 'crm/detail.html', context)


@login_required
def index(request):
    if 'assignment_id' in request.session:
        try:
            initial_event = EventAssignment.objects.get(
                pk=request.session['assignment_id']
            ).event
            if initial_event.date_begins < \
                datetime.date.today()-datetime.timedelta(weeks=4):
                initial_event = None
        except EventAssignment.DoesNotExist:
            initial_event = None
            del request.session['assignment_id']
    territory_form = SelectMyTerritoryForm(initial={'event': initial_event})
    territory_form.fields['event'].queryset = Event.objects.filter(
        eventassignment__user=request.user
    ).filter(date_begins__gte=timezone.now()-datetime.timedelta(weeks=4)
            ).order_by('-date_begins', 'number')

    # check for permission to view all records
    user = request.user
    edit_permission_ok = has_management_permission(request.user)
    context = {
        'my_territories': get_my_territories(request.user),
        'user_is_admin': edit_permission_ok,
        'territory_form': territory_form,
    }
    return render(request, 'crm/index.html', context)


@user_passes_test(has_management_permission, login_url='/crm/',
                  redirect_field_name=None)
def manage_territory(request):
    """
    Loads manage territory page as a GET request
    Also responds to form in add_conference_modal to validate/add new conference
    and reload manage_territory page with new event
    """
    conference_select_form = ConferenceSelectForm()
    new_conference_form = ConferenceEditForm()
    if request.method == 'POST':
        new_conference_form = ConferenceEditForm(request.POST)
        if new_conference_form.is_valid():
            new_event = new_conference_form.save(commit=False)
            new_event.created_by = request.user
            new_event.modified_by = request.user
            new_event.save()
            new_conference_form = ConferenceEditForm()
    context = {
        'conference_select_form': conference_select_form,
        'new_conference_form': new_conference_form
    }
    return render(request, 'crm/manage_territory.html', context)


@login_required
def new(request):
    """
    Renders new.html form to add a new contact
    """
    if request.method != 'POST':
        new_person_form = NewPersonForm()
        context = {
            'my_territories': get_my_territories(request.user),
            'new_person_form': new_person_form
        }
        return render(request, 'crm/new.html', context)

    new_person_form = NewPersonForm(request.POST)
    if not new_person_form.is_valid():
        context = {
            'my_territories': get_my_territories(request.user),
            'new_person_form': new_person_form,
        }
        return render(request, 'crm/new.html', context)
    person = new_person_form.save(commit=False)
    person.created_by=request.user
    person.modified_by=request.user
    person.save()
    add_to_recent_contacts(request, person.pk)
    return HttpResponseRedirect(reverse('crm:detail', args=(person.id,)))


@login_required
def search(request):
    """ renders search.html and/or executes advanced or quick search """
    search_form = SearchForm()
    person_list = None
    search_list = Person.objects.none()
    search_string = ''
    search_terms = None
    search_type = request.session.get('last_search_type')

    # if new search, parse relevant variables and identify search type
    if request.method == 'POST' and 'search_terms' in request.POST:
        search_type = request.session['last_search_type'] = 'quick'
        search_string = request.session['search_string'] = \
            request.POST['search_terms']
    elif request.method == 'POST':
        search_form = SearchForm(request.POST)
        search_type = request.session['last_search_type'] = 'advanced'
        search_name = request.session['search_name'] = \
            request.POST['name']
        search_name = request.session['search_name'] = request.POST['name']
        search_title = request.session['search_title'] = request.POST['title']
        search_company = request.session['search_company'] = \
            request.POST['company']
        search_prov = request.session['search_prov'] = \
            request.POST['state_province']
        search_customer = request.session['search_customer'] = \
            request.POST['past_customer']

    # if no GET parameters, assume it's a new search and set all values to None
    if request.method == 'GET' and ('page' not in request.GET
                                    and 'sort' not in request.GET):
        search_type = request.session['last_search_type'] = 'advanced'
        search_string = request.session['search_string'] = ''
        search_name = request.session['search_name'] = None
        search_title = request.session['search_title'] = None
        search_company = request.session['search_company'] = None
        search_prov = request.session['search_prov'] = None
        search_customer = request.session['search_customer'] = None
    elif request.method == 'GET':
        if search_type == None:
            search_type = 'advanced'
        search_string = request.session.get('search_string')
        search_name = request.session.get('search_name')
        search_title = request.session.get('search_title')
        search_company = request.session.get('search_company')
        search_prov = request.session.get('search_prov')
        search_customer = request.session.get('search_customer')

    # execute quick search
    if search_type == 'quick' and len(search_string.strip()) > 0 :
        search_terms = search_string.split()
        queries = []
        for term in search_terms:
            queries.append(Q(name__icontains=term))
            queries.append(Q(company__icontains=term))
        # Take one Q object from the list
        query = queries.pop()
        # OR the first Q object with the remaining ones in the list
        for item in queries:
            query |= item
        # Query the model
        search_list = Person.objects.filter(query)

    # execute advanced search
    elif search_name or search_title or search_company or search_prov:
        search_list = Person.objects.filter(name__icontains=search_name,
                                            title__icontains=search_title,
                                            company__icontains=search_company,
                                            )
        if search_prov:
            regex_val = r''
            for area_code in AC_DICT:
                if AC_DICT[area_code] == search_prov:
                    regex_val += '^' + area_code + '|^\(' + area_code + '|'
            regex_val = regex_val[:-1]
            search_list = search_list.filter(phone__regex=regex_val)
        if search_customer is not None:
            search_list = search_list.filter(
                reghistory__isnull=not search_customer)

    # Figure out sort order
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
    # If sort order not set, set to ascending by company name & set cookies
    if not sort_col:
        sort_col = 'company'
        request.session['sort_col'] = sort_col
    if not sort_order:
        sort_order = 'ASC'
        request.session['sort_order'] = sort_order
    # sort search results
    if search_list.exists():
        if sort_order == 'DESC':
            sort_col = '-' + sort_col
        search_list = search_list.order_by(sort_col)

    # paginate results
    paginator = Paginator(search_list, TERRITORY_RECORDS_PER_PAGE)
    if 'page' in request.GET:
        page = request.session['search_page'] = request.GET['page']
    else:
        page = request.session['search_page'] = 1
    try:
        person_list = paginator.page(page)
    except PageNotAnInteger:
        # if page not an integer, deliver first page
        person_list = paginator.page(1)
        page = request.session['search_page'] = 1
    except EmptyPage:
        # if page out of range, deliver last page of results
        person_list = paginator.page(paginator.num_pages)
        page = request.session['search_page'] = paginator.num_pages

    context = {
        'my_territories': get_my_territories(request.user),
        'quick_search_terms': search_string,
        'show_advanced': search_type!='quick',
        'search_form': search_form,
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
    return render(request, 'crm/search.html', context)


@login_required
def territory(request):
    if 'assignment_id' not in request.session or \
        request.session['assignment_id'] == '':
        return HttpResponseRedirect('/crm/')
    if request.method == 'POST':
        filter_form = SearchForm(request.POST)
    else:
        filter_form = SearchForm()
    event_assignment = get_object_or_404(EventAssignment,
                                         pk=request.session['assignment_id'])
    territory_list = build_user_territory_list(event_assignment, True)
    territory_list = filter_personal_territory(request, territory_list,
                                               filter_form)
    flag_list = territory_list.filter(flags__event_assignment=event_assignment)
    if 'filter_flag' in request.session:
        flag_filter_value = request.session['filter_flag']
    else:
        flag_filter_value = 'any'

    # Figure out sort order
    if 'sort' not in request.GET:
        sort_col = request.session.get('filter_sort_col')
    else:
        if request.GET['sort'] == request.session.get('filter_sort_col'):
            request.session['filter_sort_col'] = 'ASC' if \
                request.session['filter_sort_order'] == 'DESC' else 'DESC'
        else:
            request.session['filter_sort_order'] = 'ASC'
            request.session['filter_sort_col'] = request.GET['sort']
        sort_col = request.session['filter_sort_col']
    sort_order = request.session.get('filter_sort_order')
    # If sort order not set, set to ascending by company name
    if not sort_col:
        sort_col = request.session['filter_sort_col'] = 'company'
    if not sort_order:
        sort_order = request.session['filter_sort_order'] = 'ASC'
    # sort search results
    if territory_list.exists():
        if sort_order == 'DESC':
            sort_col = '-' + sort_col
        territory_list = territory_list.order_by(sort_col)

    # Paginate results
    paginator = Paginator(territory_list, TERRITORY_RECORDS_PER_PAGE)
    if 'page' in request.GET:
        page = request.session['filter_page'] = request.GET['page']
    else:
        page = request.session['filter_page'] = 1
    try:
        person_list = paginator.page(page)
    except PageNotAnInteger:
        person_list = paginator.page(1)
        page = request.session['filter_page'] = 1
    except EmptyPage:
        person_list = paginator.page(paginator.num_pages)
        page = request.session['filter_page'] = paginator.num_pages
    context = {
        'event_assignment': event_assignment,
        'my_territories': get_my_territories(request.user),
        'person_list': person_list,
        'filter_form': filter_form,
        'flag_filter_value': flag_filter_value,
        'flag_list': flag_list,
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


##################
# AJAX CALLS
##################

@login_required
def add_contact_history(request):
    person = None
    new_contact_form = NewContactForm()
    if request.method == 'POST':
        new_contact_form = NewContactForm(request.POST)
        try:
            person = Person.objects.get(pk=request.POST['person_id'])
            add_to_recent_contacts(request, request.POST['person_id'])
            if new_contact_form.is_valid():
                event = Event.objects.get(pk=request.POST['event'])
                new_contact = Contact(
                    person=person,
                    event=event,
                    date_of_contact=timezone.now(),
                    notes=new_contact_form.cleaned_data['notes'],
                    method=new_contact_form.cleaned_data['method'],
                    author=request.user,
                )
                new_contact.save()
                person.date_modified = timezone.now()
                person.modified_by = request.user
                person.save()
        except (Person.DoesNotExist, MultiValueDictKeyError):
            raise Http404('Sorry, this person seems to have been deleted ' \
                          'from the database.')
    context = {
        'person': person,
        'new_contact_form': new_contact_form,
    }
    return render(request, 'crm/addins/detail_contact_history.html', context)


@user_passes_test(has_management_permission, login_url='/crm/',
                  redirect_field_name=None)
def add_master_list_select(request):
    select_form = MasterTerritoryForm()
    list_selects = None
    sample_select = None
    select_count = 0
    if request.method == 'POST':
        try:
            event = Event.objects.get(pk=request.POST['conf_id'])
        except (Event.DoesNotExist, MultiValueDictKeyError):
            raise Http404('Something is wrong - that event does not exist')
        select_form = MasterTerritoryForm(request.POST)
        if select_form.is_valid():
            new_select = select_form.save(commit=False)
            new_select.event = event
            new_select.save()
            select_form = MasterTerritoryForm()
        list_selects = MasterListSelections.objects.filter(event=event)
        sample_select = build_master_territory_list(list_selects)
        select_count = sample_select.count()
        sample_select = sample_select.order_by('?')[:250]
        sample_select = sorted(sample_select, key=lambda o: o.company)
    context = {
        'select_form': select_form,
        'list_selects': list_selects,
        'sample_select': sample_select,
        'select_count': select_count,
    }
    return render(request, 'crm/territory_addins/master_territory_panel.html',
                  context)


@user_passes_test(has_management_permission, login_url='/crm/',
                  redirect_field_name=None)
def add_personal_list_select(request):
    select_form = PersonalTerritorySelects(filter_master_bool=True)
    list_selects = None
    sample_select = None
    select_count = 0
    if request.method == 'POST':
        event = get_object_or_404(Event, pk=request.POST['conf_id'])
        staff_member = get_object_or_404(User, pk=request.POST['staff_id'])
        event_assignment = EventAssignment.objects.get(
            user=staff_member, event=event
        )

        select_form = PersonalTerritorySelects(
            request.POST,
            filter_master_bool=event_assignment.filter_master_selects
        )
        if select_form.is_valid():
            new_select = select_form.save(commit=False)
            new_select.event_assignment = event_assignment
            new_select.save()
            select_form = PersonalTerritorySelects(
                filter_master_bool=event_assignment.filter_master_selects
            )

        list_selects = PersonalListSelections.objects.filter(
            event_assignment=event_assignment
        )

        sample_select = build_user_territory_list(event_assignment)
        select_count = sample_select.count()
        sample_select = sample_select.order_by('?')[:250]
        sample_select = sorted(sample_select, key=lambda o: o.company)
    context = {
        'filter_value': event_assignment.filter_master_selects,
        'select_form': select_form,
        'list_selects': list_selects,
        'sample_select': sample_select,
        'select_count': select_count,
    }
    return render(request, 'crm/territory_addins/personal_select_details.html',
                  context)


def add_person_to_territory(request):
    pass

@login_required
def change_flag(request):
    """
    ajax call to change flag value for an individual
    called from territory.html and from detail.html
    """
    flag = None
    if request.method != 'POST':
        return HttpResponse('')
    event_assignment = get_object_or_404(EventAssignment,
                                         pk=request.POST['event_assignment_id'])
    person = get_object_or_404(Person, pk=request.POST['person_id'])
    flag = process_flag_change(request, person, event_assignment)
    context = {
        'flag': flag,
    }
    return render(request, 'crm/territory_addins/new_flag_detail.html', context)


@login_required
def check_for_dupes(request):
    """
    AJAX call to check for possible duplicate entry when entering a new person
    called from new.html
    """
    name = title = company = city = phone = email = dupe_list = None
    if request.method == 'POST':
        name = request.POST['name']
        company = request.POST['company']
        email = request.POST['email']

        if name != '' and company != '':
            dupe_list = Person.objects.filter(name__iexact=name,
                                              company__iexact=company)
        if email != '':
            if dupe_list:
                dupe_list = dupe_list | Person.objects.filter(email=email)
            else:
                dupe_list = Person.objects.filter(email=email)
        if dupe_list and dupe_list.count() == 0:
            dupe_list = None
    context = {
        'name': name,
        'title': request.POST['title'],
        'company': request.POST['company'],
        'city': request.POST['city'],
        'phone': request.POST['phone'],
        'email': email,
        'dupe_list': dupe_list
    }
    return render(request, 'crm/addins/possible_dupe_modal.html', context)


@user_passes_test(has_management_permission, login_url='/crm/',
                  redirect_field_name=None)
def create_selection_widget(request):
    """
    Adds territory builder to manage_territory.html
    """
    if request.method != 'POST':
        return HttpResponse('')
    try:
        event = Event.objects.get(pk=request.POST['conf_id'])
    except (Event.DoesNotExist, MultiValueDictKeyError):
        raise Http404('Something is wrong - that event does not exist')
    except ValueError:
        return HttpResponse('')
    # Stuff for staff selection pane
    sales_assigned = User.objects.filter(eventassignment__event=event,
                                         eventassignment__role='SA',
                                         is_active=True)
    sponsorship_assigned = User.objects.filter(eventassignment__event=event,
                                               eventassignment__role='SP',
                                               is_active=True)
    pd_assigned = User.objects.filter(eventassignment__event=event,
                                      eventassignment__role="PD",
                                      is_active=True)
    userlist = User.objects.filter(is_active=True) \
        .exclude(id__in=sales_assigned).exclude(id__in=sponsorship_assigned) \
        .exclude(id__in=pd_assigned)

    # Stuff for master list selection pane
    select_form = MasterTerritoryForm()
    list_selects = MasterListSelections.objects.filter(event=event)
    sample_select = build_master_territory_list(list_selects)
    select_count = sample_select.count()
    sample_select = sample_select.order_by('?')[:250]
    sample_select = sorted(sample_select, key=lambda o: o.company)
    context = {
        'event': event,
        'userlist': userlist,
        'sales_assigned': sales_assigned,
        'sponsorship_assigned': sponsorship_assigned,
        'pd_assigned': pd_assigned,
        'select_form': select_form,
        'list_selects': list_selects,
        'sample_select': sample_select,
        'select_count': select_count,
    }
    return render(request, 'crm/territory_addins/territory_builder.html',
                  context)


@login_required
def delete_contact_history(request):
    person = None
    new_contact_form = NewContactForm()
    if request.method == 'POST':
        person = Person.objects.get(pk=request.POST['person_id'])
        add_to_recent_contacts(request, request.POST['person_id'])
        delete_contact = Contact.objects.get(pk=request.POST['contact_id'])
        delete_contact.delete()
    context = {
        'person': person,
        'new_contact_form': new_contact_form,
    }
    return render(request, 'crm/addins/detail_contact_history.html', context)


@user_passes_test(has_management_permission, login_url='/crm/',
                  redirect_field_name=None)
def delete_master_list_select(request):
    select_form = MasterTerritoryForm()
    list_selects = None
    sample_select = None
    select_count = 0
    if request.method == 'POST':
        try:
            event = Event.objects.get(pk=request.POST['conf_id'])
            select = MasterListSelections.objects.get(
                pk=request.POST['select_id']
            )
            select.delete()
        except (Event.DoesNotExist, MultiValueDictKeyError):
            raise Http404('Something is wrong - that event does not exist')
        except MasterListSelections.DoesNotExist:
            pass
        list_selects = MasterListSelections.objects.filter(event=event)
        sample_select = build_master_territory_list(list_selects)
        select_count = sample_select.count()
        sample_select = sample_select.order_by('?')[:250]
        sample_select = sorted(sample_select, key=lambda o: o.company)
    context = {
        'select_form': select_form,
        'list_selects': list_selects,
        'sample_select': sample_select,
        'select_count': select_count,
    }
    return render(request, 'crm/territory_addins/master_territory_panel.html',
                  context)


@user_passes_test(has_management_permission, login_url='/crm/',
                  redirect_field_name=None)
def delete_personal_list_select(request):
    select_form = PersonalTerritorySelects(filter_master_bool=True)
    list_selects = None
    sample_select = None
    select_count = 0
    if request.method == 'POST':
        event = get_object_or_404(Event, pk=request.POST['conf_id'])
        staff_member = get_object_or_404(User, pk=request.POST['staff_id'])
        event_assignment = EventAssignment.objects.get(
            user=staff_member, event=event
        )
        try:
            select = PersonalListSelections.objects.get(
                pk=request.POST['select_id']
            )
            select.delete()
        except PersonalListSelections.DoesNotExist:
            pass
        list_selects = PersonalListSelections.objects.filter(
            event_assignment=event_assignment
        )
        sample_select = build_user_territory_list(event_assignment)
        select_count = sample_select.count()
        sample_select = sample_select.order_by('?')[:250]
        sample_select = sorted(sample_select, key=lambda o: o.company)
    context = {
        'filter_value': event_assignment.filter_master_selects,
        'select_form': select_form,
        'list_selects': list_selects,
        'sample_select': sample_select,
        'select_count': select_count,
    }
    return render(request, 'crm/territory_addins/personal_select_details.html',
                  context)


@login_required
def get_recent_contacts(request):
    """ ajax call to populate recent contacts on sidebar """
    if 'recent_contacts' not in request.session:
        request.session['recent_contacts'] = []
    recent_contact_list = []
    for contact in request.session['recent_contacts']:
        try:
            recent_contact_list.append(Person.objects.get(pk=contact))
        except (Person.DoesNotExist, MultiValueDictKeyError):
            pass
    context = {
        'recent_contact_list': recent_contact_list,
    }
    return render(request, 'crm/addins/recently_viewed.html', context)


@login_required
def group_flag_update(request):
    if request.method != 'POST':
        return HttpResponse('')
    event_assignment = get_object_or_404(EventAssignment,
                                         pk=request.POST['event_assignment_id'])
    people_list = request.POST.getlist('checked_people[]')
    for person_id in people_list:
        try:
            person = Person.objects.get(pk=person_id)
            process_flag_change(request, person, event_assignment)
        except Person.DoesNotExist:
            pass
    territory_list = build_user_territory_list(event_assignment, True)
    territory_list = filter_personal_territory(request, territory_list)
    flag_list = territory_list.filter(flags__event_assignment=event_assignment)

    # sort list appropriately
    sort_col = request.session.get('filter_sort_col')
    sort_order = request.session.get('filter_sort_order')
    if not sort_col:
        sort_col = request.session['filter_sort_col'] = 'company'
    if not sort_order:
        sort_order = request.session['filter_sort_order'] = 'ASC'
    if territory_list.exists():
        if sort_order == 'DESC':
            sort_col = '-' + sort_col
        territory_list = territory_list.order_by(sort_col)

    # paginate results
    paginator = Paginator(territory_list, TERRITORY_RECORDS_PER_PAGE)
    if 'filter_page' not in request.session:
        page = request.POST.get('page', 1)
    else:
        page = request.session['filter_page']
    try:
        person_list = paginator.page(page)
    except PageNotAnInteger:
        person_list = paginator.page(1)
        page = request.session['filter_page'] = 1
    except EmptyPage:
        person_list = paginator.page(paginator.num_pages)
        page = request.session['filter_page'] = paginator.num_pages

    context = {
        'person_list': person_list,
        'flag_list': flag_list,
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
    return render(request, 'crm/territory_addins/my_territory_prospects.html',
                  context)


@user_passes_test(has_management_permission, login_url='/crm/',
                  redirect_field_name=None)
def load_staff_category_selects(request):
    """
    Loads panel showing staff members assigned to Sales, PD or Sponsorship for
    a particular event
    Called from staff-select pulldown on territory_builder.html
    """
    role_map_dict = {
        'activate-sales': ('SA', 'Sales Staff'),
        'activate-sponsorship': ('SP', 'Sponsorship Staff'),
        'activate-pd': ('PD', 'PD Staff'),
    }
    staff_group = User.objects.none()
    staff_label = None
    if request.method == 'POST':
        section_chosen = request.POST['section_chosen']
    try:
        event = Event.objects.get(pk=request.POST['conf_id'])
        staff_group = User.objects.filter(
            eventassignment__event=event,
            eventassignment__role=role_map_dict[section_chosen][0],
            is_active=True
        )
        staff_label = role_map_dict[section_chosen][1]
    except (Event.DoesNotExist, MultiValueDictKeyError, KeyError):
        pass
    context = {
        'staff_group': staff_group,
        'staff_label': staff_label,
    }
    return render(request,
                  'crm/territory_addins/personal_select_person_chooser.html',
                  context)


@user_passes_test(has_management_permission, login_url='/crm/',
                  redirect_field_name=None)
def load_staff_member_selects(request):
    """
    Loads details on a particular staff member's personal territory selects
    Called from ??? pulldown on ???
    Also called to change filter method
    """
    if request.method != 'POST':
        return HttpResponse('')
    try:
        event = Event.objects.get(pk=request.POST['event_id'])
        user = User.objects.get(pk=request.POST['user_id'])
        event_assignment = EventAssignment.objects.get(event=event, user=user)
    except Event.DoesNotExist:
        raise Http404('Something is wrong - that event no longer exists')
    except User.DoesNotExist:
        raise Http404('Something is wrong - that staff member no longer exists')
    except EventAssignment.DoesNotExist:
        raise Http404('Something is wrong - that staff member is not '
                      'assigned to this conference.')

    # Optionally process change to filter value
    if 'filter_switch' in request.POST:
        filter_switch = request.POST['filter_switch'] == 'True'
        event_assignment.filter_master_selects = filter_switch
        event_assignment.save()

    territory_select_method_form = PersonTerritorySelectMethodForm(
        instance=event_assignment
    )
    select_form = PersonalTerritorySelects(
        filter_master_bool=event_assignment.filter_master_selects
    )
    list_selects = PersonalListSelections.objects.filter(
        event_assignment=event_assignment
    )
    sample_select = build_user_territory_list(event_assignment)
    select_count = sample_select.count()
    sample_select = sample_select.order_by('?')[:250]
    sample_select = sorted(sample_select, key=lambda o: o.company)

    context={
        'filter_value': event_assignment.filter_master_selects,
        'territory_select_method_form': territory_select_method_form,
        'staff_rep': user,
        'select_form': select_form,
        'list_selects': list_selects,
        'sample_select': sample_select,
        'select_count': select_count,
    }
    return render(request, 'crm/territory_addins/filter_master_option.html',
                  context)


@login_required
def save_category_changes(request):
    updated_category_success = None
    category_form = PersonCategoryUpdateForm
    if request.method == 'POST':
        try:
            person = Person.objects.get(pk=request.POST['person_id'])
            add_to_recent_contacts(request, request.POST['person_id'])
            category_form = PersonCategoryUpdateForm(request.POST,
                                                     instance=person)
            if category_form.is_valid():
                category_form.save()
                updated_category_success = True
        except (Person.DoesNotExist, MultiValueDictKeyError):
            raise Http404('Sorry, this person seems to have been deleted ' \
                          'from the database.')
    context = {
        'updated_category_success': updated_category_success,
        'category_form': category_form,
    }
    return render(request, 'crm/addins/detail_categorize.html', context)


@login_required
def save_person_details(request):
    """ ajax call to save person details and update that section of page """
    updated_details_success = None
    person = None
    person_details_form = PersonDetailsForm()
    if request.method == 'POST':
        try:
            person = Person.objects.get(pk=request.POST['person_id'])
            add_to_recent_contacts(request, request.POST['person_id'])
            person_details_form = PersonDetailsForm(request.POST,
                                                    instance=person)
            if person_details_form.is_valid():
                person_details_form.save()
                updated_details_success = True
        except (Person.DoesNotExist, MultiValueDictKeyError):
            raise Http404('Sorry, this person seems to have been deleted ' \
                          'from the database')
    context = {
        'person': person,
        'person_details_form': person_details_form,
        'updated_details_success': updated_details_success
    }
    return render(request, 'crm/addins/person_detail.html', context)


@login_required
def select_active_conference(request):
    # context = {
    #     'my_territories': get_my_territories(request.user),
    # }
    if request.method == 'POST':
        event_assignment = get_object_or_404(EventAssignment,
                                             pk=request.POST['new_conf_id'])
        request.session['assignment_id'] = event_assignment.id
        request.session['conference_description'] = str(event_assignment.event)
        # delete all request.session cookies related to territory filter_switch
        for cookie in ['filter_page', 'filter_name', 'filter_company',
                       'filter_prov', 'filter_customer', 'filter_flag',
                       'filter_sort_col', 'filter_sort_order',
                       'filter_hide_options']:
            if cookie in request.session:
                del(request.session[cookie])
    return HttpResponse('')


@login_required
def suggest_company(request):
    """
    Ajax call (I think?) - returns json of top 25 companies (by number in db)
    that match entered string
    """
    query_term = request.GET.get('q', '')
    selects = Person.objects.filter(company__icontains=query_term) \
        .values('company').annotate(total=Count('name')) \
        .order_by('-total')[:25]
    results = []
    for select in selects:
        select_json = {}
        select_json['identifier'] = select['company']
        results.append(select_json)
    data = json.dumps(results)
    mimetype = 'applications/json'
    return HttpResponse(data, mimetype)


@login_required
def suggest_dept(request):
    """
    Ajax call (I think?) - returns json of top 25 dept matches (by number in db)
    that match entered string
    """
    query_term = request.GET.get('q', '')
    selects = Person.objects.filter(dept__icontains=query_term) \
        .values('dept').annotate(total=Count('name')) \
        .order_by('-total')[:25]
    results = []
    for select in selects:
        select_json = {}
        select_json['identifier'] = select['dept']
        results.append(select_json)
    data = json.dumps(results)
    mimetype = 'applications/json'
    return HttpResponse(data, mimetype)


@login_required
def suggest_industry(request):
    """
    Ajax call (I think?) - returns json of top 25 industry matches (by # in db)
    that match entered string
    """
    query_term = request.GET.get('q', '')
    selects = Person.objects.filter(industry__icontains=query_term) \
        .values('industry').annotate(total=Count('name')) \
        .order_by('-total')[:25]
    results = []
    for select in selects:
        select_json = {}
        select_json['identifier'] = select['industry']
        results.append(select_json)
    data = json.dumps(results)
    mimetype = 'applications/json'
    return HttpResponse(data, mimetype)


@login_required
def toggle_territory_filter(request):
    """
    Sets whether territory filter options should be hidden by default
    """
    toggle = request.GET.get('hide', False) in ['True', 'true']
    request.session['filter_hide_options'] = toggle
    return HttpResponse('')


@user_passes_test(has_management_permission, login_url='/crm/',
                  redirect_field_name=None)
def update_user_assignments(request):
    """
    ajax call to update d/b when a user is moved to a new category
    called from manage_territory.html -> territory_builder.html
    """
    role_map_dict = {
        'sales-staff': 'SA',
        'sponsorship-staff': 'SP',
        'pd-staff': 'PD',
        'unassigned-staff': 'NA',
    }
    if request.method != 'POST':
        return HttpResponse('')
    try:
        event = Event.objects.get(pk=request.POST['conf_id'])
        user = User.objects.get(pk=request.POST['user_id'])
        role = role_map_dict[request.POST['role']]
    except (Event.DoesNotExist, MultiValueDictKeyError):
        raise Http404('Something is wrong - that event does not exist')
    except User.DoesNotExist:
        raise Http404("Something is wrong - that user does not exist")
    except KeyError:
        raise Http404('Unrecognized target category')

    # if user has an assignment (and possibly sub-selects), update that record
    if EventAssignment.objects.filter(event=event, user=user).exists():
        curr_event = EventAssignment.objects.get(event=event, user=user)
        curr_event.role = role
        curr_event.save()
    # otherwise, create new assignment record
    else:
        EventAssignment(user=user, event=event, role=role).save()
    return HttpResponse('')
