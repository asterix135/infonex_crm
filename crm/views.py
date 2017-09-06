import datetime
import json
from io import BytesIO

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
from django.views.generic import DetailView, ListView, TemplateView

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate

from crm.forms import *
from crm.mixins import *
from crm.models import *
from crm.constants import *
from delegate.constants import UNPAID_STATUS_VALUES
from delegate.forms import RegDetailsForm, NewDelegateForm, CompanySelectForm, \
    AssistantForm
from marketing.mixins import GeneratePaginationList
from registration.forms import ConferenceSelectForm, ConferenceEditForm
from registration.models import RegDetails, EventOptions


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
    if not person.date_created:
        creation_date = timezone.now()
    else:
        creation_date = person.date_created
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
        date_created=creation_date,
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
        recent_contact_list = recent_contact_list[:25]
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
                  'dept': 'dept__icontains',
                  'title': 'title__icontains',}
    if for_staff_member:
        field_dict['person'] = 'pk'
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
                    if field == 'person':
                        kwargs['pk'] = list_select.person.pk
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
                if field == 'person':
                    kwargs['pk'] = list_select.person.pk
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


class Detail(DetailView):
    template_name = 'crm/detail.html'
    model = Person

    def get_context_data(self, **kwargs):
        print('get context')
        context = super(Detail, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        print('get')
        super(Detail, self).get(request, *args, **kwargs)


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
                    reg_list = reg_list | registrant.regdetails_set.all()
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
        'conf_select_form': ConferenceSelectForm(),
        'reg_details_form': RegDetailsForm(),
        'new_delegate_form': NewDelegateForm(),
        'company_select_form': CompanySelectForm(),
        'assistant_form': AssistantForm(),
    }
    return render(request, 'crm/detail.html', context)


@login_required
def index(request):
    initial_event = None
    event_assignment = None
    if 'assignment_id' in request.session:
        try:
            event_assignment = EventAssignment.objects.get(
                pk=request.session['assignment_id']
            )
            initial_event = event_assignment.event

            if initial_event.date_begins < \
                datetime.date.today()-datetime.timedelta(weeks=4):
                initial_event = None
                event_assignment = None
        except EventAssignment.DoesNotExist:
            del request.session['assignment_id']
    territory_form = SelectMyTerritoryForm(
        initial={'event_assignment': event_assignment}
    )
    territory_form.fields['event_assignment'].queryset = EventAssignment.objects.filter(
        user=request.user
    ).filter(event__date_begins__gte=timezone.now()-datetime.timedelta(weeks=4)
            ).order_by('-event__date_begins', 'event__number')

    # check for permission to view all records
    edit_permission_ok = has_management_permission(request.user)

    # if sales person, generate unpaid list
    if request.user.groups.filter(name='sales').exists() or \
        request.user.groups.filter(name='sponsorship').exists() or \
        request.user.is_superuser:
        unpaid_list = RegDetails.objects.filter(
            registration_status__in=UNPAID_STATUS_VALUES,
            invoice__sales_credit=request.user,
        ).order_by('register_date')
    else:
        unpaid_list = None
    context = {
        'my_territories': get_my_territories(request.user),
        'user_is_admin': edit_permission_ok,
        'territory_form': territory_form,
        'unpaid_list': unpaid_list,
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
        if 'assignment_id' in request.session:
            try:
                event_assignment = EventAssignment.objects.get(
                    pk=request.session['assignment_id']
                )
                master_fields = ['geo', 'main_category', 'main_category2',
                                 'dept']
                event = event_assignment.event
                form_data = {}
                general_selects = MasterListSelections.objects.filter(
                    event=event
                )
                for select in general_selects:
                    for field_name in master_fields:
                        if getattr(select, field_name) not in ('', None):
                            form_data[field_name] = getattr(select, field_name)
                            master_fields.remove(field_name)
                        if len(master_fields) == 0:
                            break
                    if len(master_fields) == 0:
                        break

                personal_fields = master_fields + ['division1', 'division2']
                personal_selects = PersonalListSelections.objects.filter(
                    event_assignment=event_assignment
                )
                for select in personal_selects:
                    for field_name in personal_fields:
                        if getattr(select, field_name) not in ('', None):
                            form_data[field_name] = getattr(select, field_name)
                            personal_fields.remove(field_name)
                        if len(personal_fields) == 0:
                            break
                    if len(personal_fields) == 0:
                        break
                new_person_form = NewPersonForm(initial=form_data)
            except EventAssignment.DoesNotExist:
                pass  # blank form is OK
        context = {
            'my_territories': get_my_territories(request.user),
            'new_person_form': new_person_form
        }
        return render(request, 'crm/new.html', context)

    if 'dupe_creation' in request.POST:
        new_person_form = NewPersonForm(initial = dict(request.POST.items()))
    else:
        new_person_form = NewPersonForm(request.POST)
    if 'dupe_creation' in request.POST or not new_person_form.is_valid():
        context = {
            'my_territories': get_my_territories(request.user),
            'new_person_form': new_person_form,
        }
        return render(request, 'crm/new.html', context)
    person = new_person_form.save(commit=False)
    person.created_by=request.user
    person.date_created = timezone.now()
    person.modified_by=request.user
    person.date_modified = timezone.now()
    person.save()

    # Add person to changes Table
    add_change_record(person, 'new')

    add_to_recent_contacts(request, person.pk)
    return HttpResponseRedirect(reverse('crm:detail', args=(person.id,)))


class Search(ListView):
    pass


@login_required
def search(request):
    """ renders search.html and/or executes advanced or quick search """
    search_form = SearchForm()
    person_list = None
    search_list = Person.objects.none()
    search_string = ''
    search_terms = None
    search_type = request.session.get('last_search_type')
    conference_select_form = ConferenceSelectForm()
    conference_select_form.fields['event'].queryset = \
        Event.objects.all().order_by('-number')
    conference_select_form.fields['event'].required = True

    # if new search, parse relevant variables and identify search type
    if request.method == 'POST' and 'search_terms' in request.POST:
        search_type = request.session['last_search_type'] = 'quick'
        search_string = request.session['search_string'] = \
            request.POST['search_terms']
    elif request.method == 'POST' and 'event' in request.POST:
        search_type = request.session['last_search_type'] = 'attendee'
        conference_select_form = ConferenceSelectForm(request.POST)
        conference_select_form.fields['event'].queryset = \
            Event.objects.all().order_by('-number')
        conf_id = request.session['search_conf_id'] = request.POST['event']
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
        if request.POST['past_customer'] == 'True':
            search_customer = request.session['search_customer'] = True
        elif request.POST['past_customer'] == 'False':
            search_customer = request.session['search_customer'] = False
        else:
            search_customer = request.session['search_customer'] = None

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
        conf_id = request.session.get('search_conf_id')

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

    # execute delegate list search
    elif search_type == 'attendee':
        search_list = Person.objects.filter(
            registrants__regdetails__conference__id=conf_id
        )
        conference_select_form = ConferenceSelectForm(
            {'event': conf_id}
        )
        conference_select_form.fields['event'].queryset = \
            Event.objects.all().order_by('-number')

    # execute advanced search
    elif (search_name and search_name not in ('', None)) or \
        (search_title and search_title not in ('', None)) or \
        (search_company and search_company not in ('', None)) or \
        (search_prov and search_prov not in ('', None)):

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
        if search_customer not in('', None):
            search_list = search_list.filter(
                registrants__isnull=not search_customer)

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
        'conference_select_form': conference_select_form,
    }
    return render(request, 'crm/search.html', context)


class Territory(GeneratePaginationList, FilterPersonalTerritory, MyTerritories,
                TerritoryList, ListView):
    template_name = 'crm/territory.html'
    paginate_by = TERRITORY_RECORDS_PER_PAGE
    context_object_name = 'person_list'
    queryset = Person.objects.none()
    form_class = SearchForm

    def dispatch(self, request, *args, **kwargs):
        """
        First entry point after as_view initializes Stuff
        Check that user has an assignment_id selected:
        If no assignment_id, redirect to base crm
        Otherwise, set self._event_assignment and proceed as normal
        """
        if 'assignment_id' not in request.session or \
            request.session['assignment_id'] == '':
            return HttpResponseRedirect('/crm/')
        else:
            self._event_assignment = get_object_or_404(
                EventAssignment,
                pk=request.session['assignment_id'],
            )
            return super(Territory, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        """
        Returns an instance of the form to be used in this view.
        """
        if form_class is None:
            form_class = self.form_class
        return form_class(**self.get_form_kwargs())

    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        return self.form_class

    def get_form_kwargs(self):
        kwargs = {
            'initial': {},
            'prefix': None,
        }
        if self.request.method == 'POST':
            kwargs.update({
                'data': self.request.POST,
            })
        else:
            form_data = {}
            if 'filter_name' in self.request.session:
                form_data['name'] = self.request.session['filter_name']
            if 'filter_title' in self.request.session:
                form_data['title'] = self.request.session['filter_title']
            if 'filter_company' in self.request.session:
                form_data['company'] = self.request.session['filter_company']
            if 'filter_prov' in self.request.session:
                form_data['prov'] = self.request.session['filter_prov']
            if 'filter_customer' in self.request.session:
                form_data['past_customer'] = \
                    self.request.session['filter_customer']
            if 'filter_dept' in self.request.session:
                form_data['dept'] = self.request.session['filter_dept']
            kwargs.update({
                'data': form_data,
            })
        return kwargs

    def _process_territory(self, request, *args, **kwargs):
        self.form = self.get_form()
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset, self.form)

        self.object_list = queryset.order_by(self.get_ordering())
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        """
        both get and post follow same logic
        """
        return self._process_territory(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        both get and post follow same logic
        """
        return self._process_territory(request, *args, **kwargs)

    def get_ordering(self):
        if 'sort' not in self.request.GET:
            sort_col = self.request.session.get('filter_sort_col')
        elif request.GET['sort'] == self.request.session.get('filter_sort_col'):
            sort_col = self.request.session['filter_sort_order'] = 'ASC' if \
                self.request.session['filter_sort_order'] == 'DESC' else 'DESC'
        else:
            self.request.session['filter_sort_order'] = 'ASC'
            sort_col = self.request.session['filter_sort_col'] = \
                       self.request.GET['sort']
        # if sort order not set, set to ascending by company name
        sort_order = self.request.session.get('filter_sort_order')
        if not sort_col:
            sort_col = self.request.session['filter_sort_col'] = 'company'
        if not sort_order:
            sort_order = self.request.session['filter_sort_order'] = 'ASC'
        if sort_order == 'DESC':
            sort_col = '-' + sort_col
        return sort_col

    def get_queryset(self):
        return self.build_user_territory_list(True)

    def paginate_queryset(self, queryset, page_size):
        return super(Territory, self).paginate_queryset(queryset, page_size)

    def get_context_data(self, **kwargs):
        context = super(Territory, self).get_context_data(**kwargs)
        context['event_assignment'] = self._event_assignment
        context['flag_list'] = self.object_list.filter(
            flags__event_assignment=self._event_assignment
        )
        if 'filter_flag' in self.request.session:
            context['flag_filter_value'] = self.request.session['filter_flag']
        else:
            context['flag_filter_value'] = 'any'
        context['filter_form'] = self.form
        context['my_territories'] = self.get_my_territories()
        context['num_records'] = self.object_list.count()
        if context['is_paginated']:
            context['pagination_list'] = self._generate_pagination_list(context)
        return context


@login_required
def territory(request):
    if 'assignment_id' not in request.session or \
        request.session['assignment_id'] == '':
        return HttpResponseRedirect('/crm/')
    if request.method == 'POST':
        filter_form = SearchForm(request.POST)
    else:
        form_data = {}
        if 'filter_name' in request.session:
            form_data['name'] = request.session['filter_name']
        if 'filter_title' in request.session:
            form_data['title'] = request.session['filter_title']
        if 'filter_company' in request.session:
            form_data['company'] = request.session['filter_company']
        if 'filter_prov' in request.session:
            form_data['state_province'] = request.session['filter_prov']
        if 'filter_customer' in request.session:
            form_data['past_customer'] = request.session['filter_customer']
        filter_form = SearchForm(form_data)
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
            request.session['filter_sort_order'] = 'ASC' if \
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
    elif 'filter_page' in request.session:
        page = request.session['filter_page']
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


class RegOptions(TemplateView):
    template_name = 'delegate/addins/conference_options.html'
    http_method_names = ['get',]

    def get(self, request, *args, **kwargs):
        self._event = get_object_or_404(Event, pk=request.GET.get('event_id', None))
        person = get_object_or_404(Person,
                                   pk=request.GET.get('person_id', None))
        if RegDetails.objects.filter(
            conference=self._event, registrant__crm_person=person
        ).count() > 0:
            return HttpResponse(status=202)
        context = self.get_context_data(**kwargs)
        return super(RegOptions, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(RegOptions, self).get_context_data(**kwargs)
        context['conference_options'] = EventOptions.objects.filter(
            event=self._event
        )
        return context


@login_required
def save_category_changes(request):
    updated_category_success = None
    category_form = PersonCategoryUpdateForm()
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


class SelectActiveConference(View):

    def get(self, request, *args, **kwargs):
        raise Http404()

    def post(self, request, *args, **kwargs):
        event_assignment = get_object_or_404(
            EventAssignment, pk=request.POST['event_assignment'])
        request.session['assignment_id'] = event_assignment.id
        request.session['conference_description'] = str(event_assignment.event)
        # delete all request.session cookies related to territory filter_switch
        for cookie in ['filter_page', 'filter_name', 'filter_company',
                       'filter_prov', 'filter_customer', 'filter_flag',
                       'filter_sort_col', 'filter_sort_order',
                       'filter_hide_options', 'territory_page']:
            if cookie in request.session:
                del(request.session[cookie])

        return HttpResponseRedirect(reverse('crm:territory'))


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
                       'filter_hide_options', 'territory_page']:
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
def toggle_person_in_territory(request):
    if request.method != 'POST':
        return HttpResponse('')
    person = get_object_or_404(Person, pk=request.POST['person_id'])
    toggle_to = request.POST['toggle_to']
    try:
        event_assignment = EventAssignment.objects.get(
            pk=request.POST['event_assignment_id']
        )
    except EventAssignment.DoesNotExist:
        return HttpResponse('')
    my_select_list = PersonalListSelections.objects.filter(
        event_assignment=event_assignment
    )
    if my_select_list.filter(person=person).exists():
        person_filter = my_select_list.get(person=person)
    else:
        person_filter = PersonalListSelections(
            person=person, event_assignment=event_assignment
        )
    person_filter.include_exclude = toggle_to
    person_filter.save()
    if toggle_to == 'add':
        try:
            flag = Flags.objects.get(person=person,
                                     event_assignment=event_assignment)
        except Flags.DoesNotExist:
            flag = None
    else:
        flag = None

    context = {
        'in_territory': toggle_to == 'add',
        'flag': flag,
        'event_assignment': event_assignment,
    }
    return render(request, 'crm/addins/detail_flag_toggle.html', context)


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


############################
# GRAPHIC ASSETS
############################
@login_required
def call_report(request):
    event_assignment = get_object_or_404(EventAssignment,
                                         pk=request.session['assignment_id'])
    event = event_assignment.event
    user = request.user
    contact_history = Contact.objects.filter(
        event=event, author=user
    ).order_by('-date_of_contact')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="call_report.pdf"'
    buffr = BytesIO()

    styles = getSampleStyleSheet()
    cell_style = styles['BodyText']
    cell_style.alignment = TA_LEFT

    report_details = []
    title = Paragraph('Call Note Report', styles['title'])
    report_details.append(title)
    conf_details_text = event.number + ': ' + event.title + ' (' \
        + user.username+ ')'
    report_details.append(Paragraph(conf_details_text, styles['h2']))
    report = SimpleDocTemplate(buffr, pagesize=letter,
                               leftMargin=inch/2, rightMargin = inch/2)
    data = []
    for contact in contact_history:
        person = contact.person.name
        if contact.person.title:
            person = person + '<br/>' + contact.person.title
        if contact.person.company:
            person = person + '<br/>' + contact.person.company
        date = Paragraph(str(contact.date_of_contact.date()), cell_style)
        person = Paragraph(person, cell_style)
        notes = Paragraph(contact.notes[:3500], cell_style)
        data.append([date, person, notes])
        table = Table(data, [inch, 3 * inch, 4.5 * inch])
        table.setStyle(TableStyle([('VALIGN', (0,0), (-1, -1), 'TOP')]))
        report_details.append(table)
        data = []
    # if len(data) > 0:
    #     call_detail_table = Table(data, [inch, 2 * inch, 4.5 * inch])
    #     call_detail_table.setStyle(TableStyle([('VALIGN', (0,0),
    #                                             (-1, -1), 'TOP')]))
    #     report_details.append(call_detail_table)


    report.build(report_details)

    pdf = buffr.getvalue()
    buffr.close()
    response.write(pdf)
    return response


class RegistrationForm(View):
    pass
