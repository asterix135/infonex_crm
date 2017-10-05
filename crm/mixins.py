import csv
import datetime

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone

from crm.constants import AC_LOOKUP, FLAG_COLORS
from crm.models import PersonalListSelections, MasterListSelections, Person, \
    EventAssignment, Flags, Changes

class ChangeRecord():

    def add_change_record(self, person, change_action):
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
            modified_by=self.request.user,
        )
        change.save()


class CsvResponseMixin():
    """
    Mixin designed to render a object_list from a ListView (or similar)
    to a csv file.
    requires 'object_list' in context and overrides default render_to_response
    By default returns all fields
    """

    filename = 'csv_download'

    def get_csv_file_details(self):
        return 'attachment; filename="' + self.filename + '.csv"'

    def render_to_response(self, context, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = self.get_csv_file_details()
        response = self.write_csv(response, context)
        return response

    def write_csv(self, response, context):
        writer = csv.writer(response)
        queryset = context['object_list']
        field_row = [f.name for f in queryset.model._meta.get_fields()
                     if not f.one_to_many]
        writer.writerow(field_row)
        for record in queryset:
            record_row = []
            for field_name in field_row:
                record_row.append(getattr(record, field_name))
            writer.writerow(record_row)
        return response


class CustomListSort():
    session_sort_vars = {'col': 'sort_col',
                         'order': 'sort_order'}

    def get_ordering(self):
        """
        Should override default method
        """
        col_val = self.session_sort_vars.get('col', 'sort_col')
        order_val = self.session_sort_vars.get('order', 'sort_order')
        sort_col = None
        sort_order = None
        if 'sort' not in self.request.GET:
            sort_col = self.request.session.get(col_val)
        elif self.request.GET['sort'] == self.request.session.get(col_val):
            sort_order = self.request.session[order_val] = 'ASC' if \
                    self.request.session[order_val] == 'DESC' else 'DESC'
            sort_col = self.request.GET['sort']
        else:
            self.request.session[order_val] = 'ASC'
            sort_col = self.request.session[col_val] = self.request.GET['sort']
        # if sort order not set, set to ascending by company name
        sort_order = self.request.session.get(order_val)
        if not sort_col:
            sort_col = self.request.session[col_val] = 'company'
        if not sort_order:
            sort_order = self.request.session[order_val] = 'ASC'
        if sort_order == 'DESC':
            sort_col = '-' + sort_col
        return sort_col


class FilterPersonalTerritory():

    def _filter_state(self, queryset):
        ac_tuple = AC_LOOKUP[self.request.session['filter_prov']]
        queries = []
        for ac in ac_tuple:
            re_term = r'^\s*\(?' + ac
            queries.append(Q(phone__iregex=re_term))
        query = queries.pop()
        for item in queries:
            query |= item
        return queryset.filter(query)

    def _filter_customer(self, queryset):
        if self.request.session['filter_customer'] == 'True':
            return queryset.filter(registrants__isnull=False).distinct()
        elif request.session['filter_customer'] == 'False':
            return queryset.filter(registrants__isnull=True)
        else:
            return queryset

    def _filter_flag(self, queryset):
        event_assignment = EventAssignment.objects.get(
            pk=self.request.session['assignment_id']
        )
        if self.request.session['filter_flag'] not in ('none', 'any'):
            return queryset.filter(
                flags__event_assignment=event_assignment,
                flags__flag=FLAG_COLORS[self.request.session['filter_flag']]
            )
        elif self.request.session['filter_flag'] == 'none':
            return queryset.exclude(
                flags__event_assignment=event_assignment
            )
        else:
            return queryset

    def _save_filters(self, filter_options, queryset, search_form):
        for option in filter_options:
            if search_form.cleaned_data[option[0]] not in ('', None):
                self.request.session[option[1]] = \
                    search_form.cleaned_data[option[0]]
            elif option[1] in self.request.session:
                del self.request.session[option[1]]
        if 'flag' in self.request.POST and self.request.POST['flag'] != 'any':
            self.request.session['filter_flag'] = self.request.POST['flag']
        elif 'filter_flag' in self.request.session:
            del self.request.session['filter_flag']

    def filter_queryset(self, territory_queryset, search_form=None):
        filter_options=(('name', 'filter_name', 'name__icontains'),
                        ('title', 'filter_title', 'title__icontains'),
                        ('company', 'filter_company', 'company__icontains'),
                        ('dept', 'filter_dept', 'dept__icontains'),
                        ('state_province', 'filter_prov'),
                        ('past_customer', 'filter_customer'))  # flag not in form
        # save form values to request.session
        if self.request.method == 'POST' and search_form and \
                search_form.is_valid():
            self._save_filters(filter_options, territory_queryset, search_form)
        # Start filtering
        kwargs = {}
        for option in filter_options[:4]:  # remainder are special cases
            if option[1] in self.request.session:
                kwargs[option[2]] = self.request.session[option[1]]
        territory_queryset = territory_queryset.filter(**kwargs)

        # Deal with state filter
        if 'filter_prov' in self.request.session and \
                self.request.session['filter_prov'] != '':
            territory_queryset = self._filter_state(territory_queryset)
        # Deal with customer filter
        if 'filter_customer' in self.request.session:
            territory_queryset = self._filter_customer(territory_queryset)
        # Deal with flag filter
        if 'filter_flag' in self.request.session and \
                'assignment_id' in self.request.session:
            territory_queryset = self._filter_flag(territory_queryset)
        return territory_queryset


class ManagementPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.groups.filter(name='db_admin').exists():
            return True
        if self.request.user.groups.filter(name='management').exists():
            return True
        if self.request.user.is_superuser:
            return True
        return False


class MyTerritories():
    def get_my_territories(self):
        return EventAssignment.objects.filter(
            user=self.request.user,
            event__date_begins__gte=timezone.now()-datetime.timedelta(weeks=4)
        ).exclude(role='NA')


class RecentContact():

    def add_to_recent_contacts(self, person_id):
        if 'recent_contacts' not in self.request.session:
            recent_contact_list = []
        else:
            recent_contact_list = self.request.session['recent_contacts']
        if person_id in recent_contact_list:
            recent_contact_list.remove(person_id)
        recent_contact_list.insert(0, person_id)
        recent_contact_list = recent_contact_list[:25]
        self.request.session['recent_contacts'] = recent_contact_list


class TerritoryListMixin(CustomListSort):
    """
    Builds a territory list.
    Note: This version has removed the ability to filter down from the
    entire database.  To get that, check the git repo prior to 2017-Sep-1
    functions build_user_territory_list and build_master_territory_list
    """
    field_dict = {'main_category': 'main_category',
                  'main_category2': 'main_category2',
                  'geo': 'geo',
                  'industry': 'industry__icontains',
                  'company': 'company__icontains',
                  'dept': 'dept__icontains',}

    def _starting_personal_territory_list(self, filter_bool):
        if filter_bool:
            return self.build_master_territory_list()
        else:
            self.user_select_set = self.user_select_set.exclude(
                include_exclude='filter'
            )
            return Person.objects.none()

    def _build_select_lists(self, queryset, list_selects, field_dict=None):
        if field_dict is None:
            field_dict = self.field_dict
        filter_selects = []
        exclude_selects = []
        for list_select in list_selects:
            kwargs = {}
            if list_select.include_exclude in ('add', 'include'):
                for field in field_dict:
                    if getattr(list_select, field) not in ('', None):
                        kwargs[field_dict[field]] = getattr(list_select, field)
                        if field == 'person':
                            kwargs['pk'] = list_select.person.pk
                query_list = Person.objects.filter(**kwargs)
                queryset = queryset | query_list
            elif list_select.include_exclude == 'filter':
                filter_selects.append(list_select)
            else:
                exclude_selects.append(list_select)
        return filter_selects, exclude_selects, queryset

    def _add_individual_selects_back_in(self, queryset, list_selects):
        for list_select in list_selects:
            if list_select.include_exclude == 'add' and list_select.person:
                add_person = Person.objects.filter(
                    pk=list_select.person.pk
                )
                queryset = queryset | add_person
        return queryset

    def _process_filters(self, filter_selects, queryset, field_dict=None):
        if field_dict is None:
            field_dict = self.field_dict
        filtered_querysets = []
        for list_select in filter_selects:
            kwargs = {}
            for field in field_dict:
                if getattr(list_select, field) not in ('', None):
                    kwargs[field_dict[field]] = getattr(list_select, field)
            filtered_querysets.append(queryset.filter(**kwargs))
        queryset = filtered_querysets.pop()
        while len(filtered_querysets) > 0:
            queryset |= filtered_querysets.pop()
        return queryset

    def _process_excludes(self, exclude_selects, queryset, field_dict=None):
        if field_dict is None:
            field_dict = self.field_dict
        for list_select in exclude_selects:
            kwargs = {}
            for field in field_dict:
                if getattr(list_select, field) not in ('', None):
                    kwargs[field_dict[field]] = getattr(list_select, field)
                    if field == 'person':
                        kwargs['pk'] = list_select.person.pk
            queryset = queryset.exclude(**kwargs)
        return queryset

    def build_user_territory_list(self, for_staff_member=False):
        field_dict = self.field_dict.copy()
        field_dict.update({'division1': 'division1',
                           'division2': 'division2',
                           'title': 'title__icontains',})
        if for_staff_member:
            field_dict['person'] = 'pk'
        filter_main = self.event_assignment.filter_master_selects
        self.user_select_set = PersonalListSelections.objects.filter(
            event_assignment=self.event_assignment
        )
        queryset = self._starting_personal_territory_list(filter_main)
        if self.user_select_set.count() == 0:
            return queryset
        filter_selects, exclude_selects, queryset = \
            self._build_select_lists(queryset, self.user_select_set, field_dict)
        if len(filter_selects) + len(exclude_selects) == 0:
            return queryset
        if len(filter_selects) > 0 and filter_main:
            queryset = self._process_filters(filter_selects,
                                             queryset,
                                             field_dict)
        if len(exclude_selects) > 0 and queryset.count() > 0:
            queryset = self._process_excludes(exclude_selects,
                                              queryset,
                                              field_dict)
        queryset = self._add_individual_selects_back_in(queryset,
                                                        self.user_select_set)
        return queryset

    def build_master_territory_list(self, list_selects=None):
        if list_selects is None:
            list_selects = MasterListSelections.objects.filter(
                event=self.event_assignment.event
            )
        queryset = Person.objects.none()
        if list_selects.count() == 0:
            return queryset
        exclude_selects, queryset = self._build_select_lists(
            queryset, list_selects
        )[1:3]
        if len(exclude_selects) == 0:
            return queryset
        return self._process_excludes(exclude_selects, queryset)


class UpdateFlag():

    def process_flag_change(self, person, event_assignment=None):
        if not event_assignment:
            event_assignment = self.event_assignment
        try:
            flag = Flags.objects.get(person=person,
                                     event_assignment=event_assignment)
        except Flags.DoesNotExist:
            flag = Flags(person=person,
                         event_assignment=event_assignment)
        if self.request.POST['flag_color'] != 'none':
            flag.flag = FLAG_COLORS[self.request.POST['flag_color']]
            if 'followup' in self.request.POST:
                flag.follow_up_date = self.request.POST['followup']
            flag.save()
        else:
            if flag.id:
                flag.delete()
            flag = None
        return flag
