from datetime import datetime, timedelta

from crm.models import Event
from registration.models import RegDetails

FREE_VALUES = ('DF', 'SD', 'G')

class CurrentRegistrationCounts:
    def _list_start_date(self):
        today = datetime.today()
        return today - timedelta(days=today.weekday())

    def _list_end_date(self):
        today = datetime.today()
        return today + timedelta(weeks=26)

    def get_current_reg_counts(self):
        upcoming_events = Event.objects.filter(
            date_begins__gte=self._list_start_date(),
            date_begins__lte=self._list_end_date()
        ).order_by('date_begins')
        reg_count_list = []
        for event in upcoming_events:
            event_registration_set = RegDetails.objects.filter(
                conference=event.id
            )
            paid_count = event_registration_set.filter(
                registration_status='DP'
            ).count()
            unpaid_count = event_registration_set.filter(
                registration_status='DU'
            ).count()
            free_count = event_registration_set.filter(
                registration_status__in=FREE_VALUES
            ).count()
            reg_count_list.append({
                'event': f'{event.number} - {event.title}',
                'start_date': event.date_begins.strftime('%b-%d-%Y'),
                'paid_count': paid_count,
                'unpaid_count': unpaid_count,
                'free_count': free_count,
                'total_count': paid_count + unpaid_count + free_count,
            })

        return reg_count_list
