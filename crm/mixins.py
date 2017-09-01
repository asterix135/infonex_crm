from crm.models import PersonalListSelections, MasterListSelections, Person


class TerritoryList():
    """
    Builds a territory list.
    Note: This version has removed the ability to filter down from the
    entire database.  To get that, check the git repo prior to 2017-Sep-1
    functions build_user_territory_list and build_master_territory_list
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

    def _starting_personal_territory_list(self, filter_bool):
        if filter_bool:
            return self.build_user_territory_list()
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
            if list_select.include_exclude == 'add':
                for field in field_dict:
                    if getattr(list_select, field) not in ('', None):
                        kwargs[field_dict[field]] = getattr(list_select, field)
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
            queryset = queryset.exclude(**kwargs)
        return queryset

    def build_user_territory_list(self, for_staff_member=False):
        field_dict = self.field_dict.copy()
        field_dict.update({'division1': 'division1',
                           'division2': 'division2',
                           'title': 'title__icontains'})
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

    def build_master_territory_list(self):
        list_selects = MasterListSelections.objects.filter(
            event=self.event_assignment.event
        )
        queryset = Person.objects.none
        if list_selects.count() == 0:
            return queryset
        exclude_selects, queryset = self._build_select_lists(
            queryset, list_selects
        )[1:2]
        if len(exclude_selects) == 0:
            return queryset
        return self._process_excludes(exclude_selects, queryset)
