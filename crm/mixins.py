import datetime

from django.db.models import Q
from django.utils import timezone

from crm.constants import AC_LOOKUP, FLAG_COLORS
from crm.models import PersonalListSelections, MasterListSelections, Person, \
    EventAssignment, Flags


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


class MyTerritories():
    def get_my_territories(self):
        return EventAssignment.objects.filter(
            user=self.request.user,
            event__date_begins__gte=timezone.now()-datetime.timedelta(weeks=4)
        ).exclude(role='NA')


class UpdateFlag():
    def process_flag_change(self, person, event_assignment=None):
        if not event_assignment:
            event_assignment = self._event_assignment
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


class TerritoryList():
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
        filter_main = self._event_assignment.filter_master_selects
        self.user_select_set = PersonalListSelections.objects.filter(
            event_assignment=self._event_assignment
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
        return queryset

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

    def build_master_territory_list(self):
        list_selects = MasterListSelections.objects.filter(
            event=self._event_assignment.event
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
