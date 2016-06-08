import datetime
from django.utils import timezone
from django.test import TestCase
from .models import Person
from django.core.urlresolvers import reverse


class PersonMethodTests(TestCase):

    def test_was_added_recently_with_future_created_date(self):
        """
        was_added_recently() should return False for persons whose created_date
        is in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_person = Person(created_date=time)
        self.assertEqual(future_person.was_added_recently(), False)

    def test_was_modified_recently_with_future_last_modified(self):
        """
        was_modified_recently() should return False for persons whose
        last_modified is in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_person = Person(last_modified=time)
        self.assertEqual(future_person.was_modified_recently(), False)

    def test_was_added_recently_with_old_added_date(self):
        """
        was_added_recently() should return False for persons whose created_date
        is older than 14 days
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_person = Person(created_date=time)
        self.assertEqual(old_person.was_added_recently(), False)

    def test_was_modified_recently_with_old_last_modified(self):
        """
        was_modified_recently() should return False for persons whose
        last_modified is older than 14 days
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_person = Person(last_modified=time)
        self.assertEqual(old_person.was_modified_recently(), False)

    def test_was_added_recently_with_recent_added_date(self):
        """
        was_added_recently() should return True for persons whose created_date
        is within 14 days
        """
        time = timezone.now() - datetime.timedelta(days=10)
        recent_person = Person(created_date=time)
        self.assertEqual(recent_person.was_added_recently(), True)

    def test_was_modified_recently_with_recent_added_date(self):
        """
        was_added_recently() should return True for persons whose
        last_modified is within 14 days
        """
        time = timezone.now() - datetime.timedelta(days=10)
        recent_person = Person(last_modified=time)
        self.assertEqual(recent_person.was_modified_recently(), True)


def create_person(person_fname, person_lname, person_co, days):
    """
    Creates a person with given first name, last name & company and created
    and modified the given number of 'days' offset to now (negative for past
    created, postive for future created)
    :param person_fname: string
    :param person_lname: string
    :param person_co: string
    :param days: integer
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Person.objects.create(first_name=person_fname,
                                 last_name=person_lname,
                                 company=person_co,
                                 created_date=time,
                                 last_modified=time)


class PersonViewTests(TestCase):
    def test_index_view_with_no_people(self):
        """
        If no persons exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('crm:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No people available.')
        self.assertQuerysetEqual(response.context['latest_person_list'], [])

    def test_index_with_a_past_person(self):
        """
        Persons with a created date in the past should be displayed on the
        index page.
        """
        create_person(person_fname='First', person_lname='Last',
                      person_co="Company", days=-10)
        response = self.client.get(reverse('crm:index'))
        self.assertQuerysetEqual(
            response.context['latest_person_list'],
            ['<Person: First Last, Company>']
        )

    def test_index_view_with_a_future_person(self):
        """
        Persons with a creation date in the future should not be displayed on
        the index page.
        """
        create_person(person_fname='First', person_lname='Last',
                      person_co="Company", days=10)
        response = self.client.get(reverse('crm:index'))
        self.assertContains(response, 'No people available.',
                            status_code=200)
        self.assertQuerysetEqual(
            response.context['latest_person_list'], [])

    def test_index_view_with_future_and_past_person(self):
        """
        Even if past and future-dated persons exist, only past persons should
        be displayed.
        """
        create_person(person_fname='First1', person_lname='Last1',
                      person_co="Company1", days=-10)
        create_person(person_fname='First2', person_lname='Last2',
                      person_co="Company2", days=10)
        response = self.client.get(reverse('crm:index'))
        self.assertQuerysetEqual(
            response.context['latest_person_list'],
            ['<Person: First1 Last1, Company1>']
        )

    def test_index_view_with_two_past_people(self):
        """
        The persons index page may display multiple people
        """
        create_person(person_fname='First1', person_lname='Last1',
                      person_co="Company1", days=-10)
        create_person(person_fname='First2', person_lname='Last2',
                      person_co="Company2", days=-5)
        response = self.client.get(reverse('crm:index'))
        self.assertQuerysetEqual(
            response.context['latest_person_list'],
            ['<Person: First2 Last2, Company2>',
             '<Person: First1 Last1, Company1>']
        )
