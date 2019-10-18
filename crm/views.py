import datetime
import json
import re
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
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate

from crm.constants import *
from crm.forms import *
from crm.mixins import *
from crm.models import *
from crm.pdfs import RegFormPdf
from delegate.constants import UNPAID_STATUS_VALUES
from delegate.forms import RegDetailsForm, NewDelegateForm, CompanySelectForm, \
    AssistantForm
from delegate.mixins import PdfResponseMixin
from delegate.models import QueuedOrder
from marketing.mixins import GeneratePaginationList
from registration.forms import ConferenceSelectForm, ConferenceEditForm
from registration.models import RegDetails, EventOptions


##################
# HELPER FUNCTIONS
##################

def add_change_record(person, change_action, user):
    """
    Being Replaced by Mixin ChangeRecord
    Still needs to be updated:
    def delete
    def new

    updates/changes/deletes
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
        modified_by=user,
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


def get_my_territories(user):
    """
    returns queryset of active EventAssignments for a user
    to be replaced by MyTerritories mixin in:
    - index
    - new
    - search
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
    replaced by Mixin TerritoryListMixin
    needs to be updated in:
    - add_master_list_select
    - build_user_territory_list
    - delete_master_list_select
    """
    field_dict = {'main_category': 'main_category',
                  'main_category2': 'main_category2',
                  'geo': 'geo',
                  'industry': 'industry__icontains',
                  'company': 'company__icontains',
                  'dept': 'dept__icontains',
                  'title': 'title__icontains',}
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
    being replaced by mixin TerritoryListMixin.  Needs updating in:
    - add_personal_list_select
    - delete_personal_list_select
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
    Replacing with ManagementPermissionMixin

    used in def index (not as decorator)
    used in def manage_territory
    used in def add_master_list_select
    used in def add_personal_list_select
    used in def create_selection_widget
    used in def delete_master_list_select
    used in def delete_personal_list_select
    used in def load_staff_category_selects
    used in def load_staff_member_selects
    used in def update_user_assignments

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
    add_change_record(person, 'delete', request.user)
    person.delete()
    return HttpResponseRedirect('/crm/search/')


class Detail(RecentContact, MyTerritories, TerritoryListMixin, DetailView):
    context_object_name = 'person'
    template_name = 'crm/detail.html'
    model = Person
    flag = None
    in_territory = False
    event_assignment = None
    session_sort_vars = {'col': 'filter_sort_col',
                         'order': 'filter_sort_order'}

    def _build_reg_list(self):
        reg_list = None
        if self.object.registrants_set.exists():
            for registrant in self.object.registrants_set.all():
                if not reg_list:
                    reg_list = registrant.regdetails_set.all()
                else:
                    reg_list = reg_list | registrant.regdetails_set.all()
            if reg_list.count() == 0:
                return None
            return reg_list.order_by('-register_date')
        return None

    def _update_territory_specfics(self):
        try:
            self.event_assignment = EventAssignment.objects.get(
                pk=self.request.session['assignment_id']
            )
            my_territory = self.build_user_territory_list(True)
            self.in_territory = self.object in my_territory
            if self.in_territory:
                try:
                    self.flag = Flags.objects.get(
                        person=self.object,
                        event_assignment=self.event_assignment
                    )
                except Flags.DoesNotExist:
                    pass  # default flag=False is fine
        except EventAssignment.DoesNotExist:
            pass  # default values are fine

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.add_to_recent_contacts(self.kwargs.get(self.pk_url_kwarg))
        if 'assignment_id' in request.session:
            self._update_territory_specfics()

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        # various forms needed in page
        context['conf_select_form'] = ConferenceSelectForm()
        context['reg_details_form'] = CrmRegDetailsForm()
        context['new_delegate_form'] = NewDelegateForm()
        context['company_select_form'] = CompanySelectForm()
        context['assistant_form'] = AssistantForm()
        context['new_contact_form'] = NewContactForm()
        context['person_details_form'] = PersonDetailsForm(
            instance=self.object
        )
        context['category_form'] = PersonCategoryUpdateForm(
            instance=self.object
        )
        # other data to be passed
        context['my_territories'] = self.get_my_territories()
        context['reg_list'] = self._build_reg_list()
        context['flag'] = self.flag
        context['in_territory'] = self.in_territory
        context['event_assignment'] = self.event_assignment
        return context


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


class ManageTerritory(ManagementPermissionMixin, FormView):
    template_name = 'crm/manage_territory.html'
    form_class = ConferenceEditForm

    def form_valid(self, form):
        """
        Override because we don't want to redirect.
        Also, becasue we actually want to save imput
        """
        new_event = form.save(commit=False)
        new_event.created_by = self.request.user
        new_event.modified_by = self.request.user
        new_event.save()
        form = self.form_class()
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(ManageTerritory, self).get_context_data(**kwargs)
        context['new_conference_form'] = context.pop('form')
        context['conference_select_form'] = ConferenceSelectForm()
        return context


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
    add_change_record(person, 'new', request.user)

    add_to_recent_contacts(request, person.pk)
    return HttpResponseRedirect(reverse('crm:detail', args=(person.id,)))


class Search(CustomListSort, GeneratePaginationList, MyTerritories, ListView):
    template_name = 'crm/search.html'
    context_object_name = 'person_list'
    queryset = Person.objects.none()
    paginate_by = TERRITORY_RECORDS_PER_PAGE
    search_string = None
    search_form = SearchForm()
    conference_select_form = ConferenceSelectForm()
    session_sort_vars = {'col': 'sort_col',
                         'order': 'sort_order'}

    def _execute_advanced_search(self, search_params, *args, **kwargs):
        # make sure there is something to search
        if (search_params['name'] in ('', None) and
            search_params['title'] in ('', None) and
            search_params['dept'] in ('', None) and
            search_params['company'] in ('', None) and
            search_params['prov'] in ('', None) and
            search_params['customer'] in ('', None) and
            search_params['phone_number'] in ('', None)):
            return self.new_search(self.request, *args, **kwargs)
        self.queryset = Person.objects.filter(
            (Q(name__icontains=search_params['name']) &
            Q(title__icontains=search_params['title']) &
            Q(company__icontains=search_params['company']) &
            Q(dept__icontains=search_params['dept'])) &
            (Q(phone__icontains=search_params['phone_number']) |
             Q(phone_main__icontains=search_params['phone_number']) |
             Q(phone_alternate__icontains=search_params['phone_number']))
        )
        if search_params['prov'] not in ('', None):
            regex_val = r''
            for area_code in AC_DICT:
                if AC_DICT[area_code] == search_params['prov']:
                    regex_val += '^' + area_code + '|^\(' + area_code + '|'
            regex_val = regex_val[:-1]
            self.queryset = self.queryset.filter(phone__regex=regex_val)
        if search_params['customer'] not in ('', None):
            self.queryset = self.queryset.filter(
                registrants__isnull = (search_params['customer'] in ('False', False))
            )
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(**kwargs))

    def _execute_attendee_search(self, **kwargs):
        # Update self.queryset first so can use default methods
        self.queryset = Person.objects.filter(
            registrants__regdetails__conference__id=self.conf_id
        )
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(**kwargs))

    def _execute_quick_search(self, request, *args, **kwargs):
        # Only execute if there is actually text in the search string
        if len(self.search_string.strip()) == 0:
            return self.new_search(request, *args, **kwargs)
        search_term = self.search_string.strip()
        search_term = re.sub(' +', ' ', search_term)
        query = Q(name__icontains=search_term)
        query |= Q(company__icontains=search_term)
        query |= Q(title__icontains=search_term)

        # Update self.queryset first so can use default methods
        self.queryset = Person.objects.filter(query)
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(**kwargs))

    def advanced_search(self, request, *args, **kwargs):
        self.search_form = SearchForm(request.GET)  # TODO: CHECK THIS IS OK
        self.search_type = request.session['last_search_type'] = 'advanced'
        search_params = {}
        search_params['name'] = request.session['search_name'] = \
                request.GET['name']
        search_params['title'] = request.session['search_title'] = \
                request.GET['title']
        search_params['dept'] = request.session['search_dept'] = \
                request.GET['dept']
        search_params['company'] = request.session['search_company'] = \
                request.GET['company']
        search_params['prov'] = request.session['search_prov'] = \
                request.GET['state_province']
        search_params['phone_number'] = request.session['phone_number'] = \
                request.GET['phone_number']
        if request.GET['past_customer'] in ('True', 'False'):
            search_params['customer'] = \
                request.session['search_customer'] = \
                request.GET['past_customer']
        else:
            search_params['customer'] = \
                    request.session['search_customer'] = None
        return self._execute_advanced_search(search_params, *args, **kwargs)

    def attendee_search(self, request, *args, **kwargs):
        self.search_type = request.session['last_search_type'] = 'attendee'
        self.conference_select_form = ConferenceSelectForm(request.GET)
        self.conf_id = request.session['search_conf_id'] = request.GET['event']
        return self._execute_attendee_search(**kwargs)

    def get(self, request, *args, **kwargs):
        self.search_type = request.session.get('last_search_type')
        if 'search_terms' in request.GET:
            return self.quick_search(request, *args, **kwargs)
        if 'event' in request.GET:
            return self.attendee_search(request, *args, **kwargs)
        if 'name' in request.GET:
            return self.advanced_search(request, *args, **kwargs)
        if ('page' not in request.GET and 'sort' not in request.GET):
            return self.new_search(request, *args, **kwargs)
        return self.old_search(request, *args, **kwargs)

    def new_search(self, request, *args, **kwargs):
        self.search_type = request.session['last_search_type'] = 'advanced'
        request.session['search_string'] = ''
        search_params = {}
        search_params['name'] = request.session['search_name'] = None
        search_params['title'] = request.session['search_title'] = None
        search_params['dept'] = request.session['search_dept'] = None
        search_params['company'] = request.session['search_company'] = None
        search_params['prov'] = request.session['search_prov'] = None
        search_params['customer'] = request.session['search_customer'] = None
        search_params['phone_number'] = request.session['phone_number'] = None
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(**kwargs))

    def old_search(self, request, *args, **kwargs):
        if not self.search_type:
            self.search_type = 'advanced'
        # This doesn't all need to be done, but it's O(1) so is ok
        self.search_string = request.session.get('search_string')
        search_params = {}
        search_params['name'] = request.session.get('search_name')
        search_params['title'] = request.session.get('search_title')
        search_params['dept'] = request.session.get('search_dept')
        search_params['company'] = request.session.get('search_company')
        search_params['prov'] = request.session.get('search_prov')
        search_params['customer'] = request.session.get('search_customer')
        search_params['phone_number'] = request.session.get('phone_number')
        self.conf_id = request.session.get('search_conf_id')
        if self.search_type == 'advanced':
            return self._execute_advanced_search(search_params, *args, **kwargs)
        if self.search_type == 'quick':
            return self._execute_quick_search(request, *args, **kwargs)
        if self.search_type == 'attendee':
            return self._execute_attendee_search(**kwargs)
        return self.new_search(request, *args, **kwargs)

    def quick_search(self, request, *args, **kwargs):
        self.search_type = request.session['last_search_type'] = 'quick'
        self.search_string = request.session['search_string'] = \
                request.GET['search_terms']
        return self._execute_quick_search(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Search, self).get_context_data(**kwargs)
        context['my_territories'] = self.get_my_territories()
        if context['is_paginated']:
            context['pagination_list'] = self.generate_pagination_list(context)
        context['search_form'] = self.search_form

        # TODO: the next 2 lines shouldn't be here - figure out where to put it
        self.conference_select_form.fields['event'].queryset = \
                Event.objects.all().order_by('-number')
        self.conference_select_form.fields['event'].required = True

        context['conference_select_form'] = self.conference_select_form
        context['quick_search_term'] = self.search_string
        context['show_advanced'] = self.search_type != 'quick'
        return context


class Territory(GeneratePaginationList, FilterPersonalTerritory, MyTerritories,
                TerritoryListMixin, ListView):
    template_name = 'crm/territory.html'
    paginate_by = TERRITORY_RECORDS_PER_PAGE
    context_object_name = 'person_list'
    queryset = Person.objects.none()
    form_class = SearchForm
    session_sort_vars = {'col': 'filter_sort_col',
                         'order': 'filter_sort_order'}

    def dispatch(self, request, *args, **kwargs):
        """
        First entry point after as_view initializes Stuff
        Check that user has an assignment_id selected:
        If no assignment_id, redirect to base crm
        Otherwise, set self.event_assignment and proceed as normal
        """
        if 'assignment_id' not in request.session or \
            request.session['assignment_id'] == '':
            return HttpResponseRedirect('/crm/')
        else:
            self.event_assignment = get_object_or_404(
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

    def is_company_list(self, request):
        if 'view' in request.GET and request.GET['view'] == 'company':
            return True
        return False

    def _process_territory(self, request, *args, **kwargs):
        self.form = self.get_form()
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset, self.form)
        self.company_view = self.is_company_list(request)
        if self.company_view:
            self.object_list = queryset.values('company').order_by('company'). \
                    annotate(num_records=Count('company'))
        else:
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

    def get_queryset(self):
        return self.build_user_territory_list(True)

    def get_context_data(self, **kwargs):
        context = super(Territory, self).get_context_data(**kwargs)
        context['event_assignment'] = self.event_assignment
        context['flag_list'] = self.object_list.filter(
            flags__event_assignment=self.event_assignment
        )
        if 'filter_flag' in self.request.session:
            context['flag_filter_value'] = self.request.session['filter_flag']
        else:
            context['flag_filter_value'] = 'any'
        context['filter_form'] = self.form
        context['my_territories'] = self.get_my_territories()
        context['num_records'] = self.object_list.count()
        context['company_view'] = self.company_view
        if context['is_paginated']:
            context['pagination_list'] = self.generate_pagination_list(context)
        return context


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
    return render(request, 'crm/detail_addins/detail_contact_history.html', context)


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


class ChangeFlag(UpdateFlag, TemplateView):
    template_name = 'crm/territory_addins/new_flag_detail.html'
    http_method_name = ['get',]

    def post(self, request, *args, **kwargs):
        self.event_assignment = get_object_or_404(
            EventAssignment, pk=request.POST['event_assignment_id']
        )
        person = get_object_or_404(Person, pk=request.POST['person_id'])
        self.flag = self.process_flag_change(person)
        context = self.get_context_data(**kwargs)
        return super(ChangeFlag, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ChangeFlag, self).get_context_data(**kwargs)
        context['flag'] = self.flag
        return context


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


class CreateSelectionWidget(ManagementPermissionMixin, TerritoryListMixin,
                            FormMixin, DetailView):
    template_name = 'crm/territory_addins/territory_builder.html'
    context_object_name = 'event'
    model = Event
    form_class = MasterTerritoryForm

    def _add_staff_selection_details_to_context(self, context):
        sales_assigned = User.objects.filter(
            eventassignment__event=self.object,
            eventassignment__role='SA',
            is_active=True
        )
        sponsorship_assigned = User.objects.filter(
            eventassignment__event=self.object,
            eventassignment__role='SP',
            is_active=True
        )
        pd_assigned = User.objects.filter(
            eventassignment__event=self.object,
            eventassignment__role="PD",
            is_active=True
        )
        userlist = User.objects.filter(is_active=True) \
                .exclude(id__in=sales_assigned) \
                .exclude(id__in=sponsorship_assigned) \
                .exclude(id__in=pd_assigned) \
                .order_by('username')
        context['userlist'] = userlist
        context['sales_assigned'] = sales_assigned
        context['sponsorship_assigned'] = sponsorship_assigned
        context['pd_assigned'] = pd_assigned
        return context

    def _add_master_list_details_to_context(self, context):
        list_selects = MasterListSelections.objects.filter(event=self.object)
        sample_select = self.build_master_territory_list(list_selects)
        context['list_selects'] = list_selects
        context['select_count'] = sample_select.count()
        sample_select = sample_select.order_by('?')[:250]
        sample_select = sorted(sample_select, key=lambda o: o.company)
        context['sample_select'] = sample_select
        return context

    def get_context_data(self, **kwargs):
        context = super(CreateSelectionWidget, self).get_context_data(**kwargs)
        context = self._add_staff_selection_details_to_context(context)
        context = self._add_master_list_details_to_context(context)
        context['select_form'] = context.pop('form')
        return context


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
    return render(request, 'crm/detail_addins/detail_contact_history.html', context)


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


class ExportListSelects(ManagementPermissionMixin, CsvResponseMixin,
                        TerritoryListMixin, SingleObjectMixin, ListView):
    model = EventAssignment

    def get(self, request, *args, **kwargs):
        self.event_assignment = self.object = self.get_object(
            queryset=self.model._default_manager.all()
        )
        return super(ExportListSelects, self).get(request, *args, **kwargs)

    def get_csv_file_details(self):
        details = 'attachment; filename="list_selects_'
        details += self.event_assignment.event.number + '_'
        details += self.event_assignment.user.username + '.csv"'
        return details

    def get_queryset(self):
        return self.build_user_territory_list()


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


class GroupFlagUpdate(GeneratePaginationList, FilterPersonalTerritory,
                      TerritoryListMixin, UpdateFlag, ListView):
    template_name = 'crm/territory_addins/my_territory_prospects.html'
    paginate_by = TERRITORY_RECORDS_PER_PAGE
    context_object_name = 'person_list'
    queryset = Person.objects.none()
    session_sort_vars = {'col': 'filter_sort_col',
                         'order': 'filter_sort_order'}

    def _process_flag_list(self, people_list):
        for person_id in people_list:
            try:
                person = Person.objects.get(pk=person_id)
                self.process_flag_change(person)
            except Person.DoesNotExist:
                pass

    def post(self, request, *args, **kwargs):
        self.event_assignment = get_object_or_404(
            EventAssignment, pk=request.POST['event_assignment_id']
        )
        people_list = request.POST.getlist('checked_people[]')
        self._process_flag_list(people_list)
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        self.object_list = queryset.order_by(self.get_ordering())
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_queryset(self):
        return self.build_user_territory_list(True)

    def get_context_data(self, **kwargs):
        context = super(GroupFlagUpdate, self).get_context_data(**kwargs)
        context['event_assignment'] = self.event_assignment
        context['flag_list'] = self.object_list.filter(
            flags__event_assignment=self.event_assignment
        )
        if context['is_paginated']:
            context['pagination_list'] = self.generate_pagination_list(context)
        return context


class LoadStaffCategorySelects(ManagementPermissionMixin, TemplateView):
    template_name = 'crm/territory_addins/personal_select_person_chooser.html'

    def get_context_data(self, **kwargs):
        role_map_dict = {'SA': 'Sales Staff',
                         'SP': 'Sponsorship Staff',
                         'PD': 'PD Staff'}
        context = super(LoadStaffCategorySelects, self) \
                    .get_context_data(**kwargs)
        event = Event.objects.get(pk=self.request.GET['conf_id'])
        section_chosen = self.request.GET['section_chosen']
        context['staff_label'] = role_map_dict[section_chosen]
        context['staff_group'] = User.objects.filter(
            eventassignment__event=event,
            eventassignment__role=section_chosen
        )
        return context


class LoadStaffMemberSelects(ManagementPermissionMixin, TerritoryListMixin,
                             ListView):
    template_name = 'crm/territory_addins/filter_master_option.html'
    context_object_name = 'list_selects'
    model = PersonalListSelections

    def _get_forms(self):
        form_dict = {}
        form_dict['select_form'] = PersonalTerritorySelects(
            filter_master_bool=self.event_assignment.filter_master_selects
        )
        form_dict['territory_select_method_form'] = \
                PersonTerritorySelectMethodForm(instance=self.event_assignment)
        return form_dict

    def _get_sample_select(self):
        sample_select_data = {}
        sample_select = self.build_user_territory_list(True)
        sample_select_data['select_count'] = sample_select.count()
        sample_select = sample_select.order_by('?')[:250]
        sample_select = sorted(sample_select, key=lambda o: o.company)
        sample_select_data['sample_select'] = sample_select
        return sample_select_data

    def _process_filter_switch(self):
        filter_switch = self.request.GET['filter_switch'] == 'True'
        self.event_assignment.filter_master_selects = filter_switch
        self.event_assignment.save()

    def get(self, request, *args, **kwargs):
        event = Event.objects.get(pk=request.GET['event_id'])
        self.user = User.objects.get(pk=request.GET['user_id'])
        self.event_assignment = EventAssignment.objects.get(
            event=event, user=self.user
        )
        if 'filter_switch' in request.GET:
            self._process_filter_switch()
        return super(LoadStaffMemberSelects, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LoadStaffMemberSelects, self).get_context_data(**kwargs)
        context['filter_value'] = self.event_assignment.filter_master_selects
        context['staff_rep'] = self.user
        context['event_assignment'] = self.event_assignment
        context.update(self._get_forms())
        context.update(self._get_sample_select())
        return context

    def get_queryset(self):
        return self.model.objects.filter(event_assignment=self.event_assignment)


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
    return render(request, 'crm/detail_addins/detail_categorize.html', context)


@login_required
def save_person_details(request):
    """ ajax call to save person details and update that section of page """
    updated_details_success = None
    person = None
    person_details_form = PersonDetailsForm()
    if request.method == 'POST':
        try:
            person = Person.objects.get(pk=request.POST['person_id'])
            add_change_record(person, 'update', request.user)
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
    return render(request, 'crm/detail_addins/person_detail_edit_panel.html', context)


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


class SubmitRegistration(View):
    def post(self, request, *args, **kwargs):
        person = Person.objects.all()[0]
        event = Event.objects.all()[Event.objects.all().count() - 1]
        rep = User.objects.all()[0]
        queued_order = QueuedOrder(
            crm_person=person,
            salutation='Mr.',
            first_name='Donald',
            last_name='Duck',
            title='Quacker',
            email1='donald@duck.com',
            phone1='416-555-1212',
            company_name='Disney on Ice',
            address1='123 Main Street',
            city='Disneyland',
            state_prov='CA',
            postal_code='99666',
            conference=event,
            registration_status='K',
            registration_notes='Hard to understand this guy',
            sales_credit=rep,
        )
        queued_order.save()
        return HttpResponse()


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


class RegistrationForm(PdfResponseMixin, DetailView):
    model = Person

    def get_addl_details(self, request):
        reg_detail_dict = {}
        for field_name in REG_FORM_FIELDS:
            if field_name[1] == 'val':
                reg_detail_dict[field_name[0]] = request.GET.get(field_name[0])
            else:  # currently only for int_list - can expand if needed
                list_contents = request.GET.get(field_name[0])
                list_contents = [int(x.strip())
                                 for x in list_contents.split(',')
                                 if x != '']
                reg_detail_dict[field_name[0]] = list_contents
        return reg_detail_dict

    def get_conference(self):
        return Event.objects.get(pk=self.request.GET.get('event'))

    def get_pdf_name(self):
        return self.object.name + '_reg_form_' + self.conference.number

    def get_context_data(self, **kwargs):
        context = super(RegistrationForm, self).get_context_data(**kwargs)
        report = RegFormPdf(self.conference,
                            self.request.user, self.addl_details)
        context['pdf'] = report.generate_report()
        return context

    def get(self, request, *args, **kwargs):
        self.conference = self.get_conference()
        self.addl_details = self.get_addl_details(request)
        return super(RegistrationForm, self).get(request, *args, **kwargs)
