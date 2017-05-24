import datetime
import re

from django.db import models
from django.utils import timezone
from .constants import *


# OK PER OVERHAUL
class Person(models.Model):
    """
    Basic person model
    """
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    url = models.URLField(max_length=200, blank=True)
    linkedin = models.URLField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    phone_main = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    do_not_email = models.BooleanField(default=False)
    do_not_call = models.BooleanField(default=False)
    city = models.CharField(max_length=50, blank=True)
    dept = models.CharField(max_length=50, blank=True, null=True)  # General area of job
    industry = models.TextField(blank=True)  # free-form descripton
    geo = models.CharField(max_length=20,
                           choices=GEO_CHOICES,
                           default='Unknown')
    main_category = models.CharField(max_length=25,
                                     choices=CAT_CHOICES,
                                     default='Industry')  # f1 in original db
    main_category2 = models.CharField(max_length=15,
                                      choices=CAT_CHOICES,
                                      default='NA')
    division1 = models.CharField(max_length=20,
                                 choices=DIV_CHOICES,
                                 default='NA')  # for splitting leads
    division2 = models.CharField(max_length=20,
                                 choices=DIV_CHOICES,
                                 default='NA',
                                 blank=True)  # for splitting leads
    date_created = models.DateTimeField('date created')
    created_by = models.ForeignKey('auth.User',
                                   default=1,
                                   related_name='person_created_by')
    date_modified = models.DateTimeField('date modified')
    modified_by = models.ForeignKey('auth.User',
                                    default=1,
                                    related_name='person_modifed_by')

    def __str__(self):
        return self.name + ' ' + ', ' + self.company

    def was_added_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=14) <= self.date_created <= now
    was_added_recently.admin_order_field = 'created_date'
    was_added_recently.boolean = True
    was_added_recently.short_description = 'Added recently?'

    def was_modified_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=14) <= self.date_modified <= now
    was_modified_recently.admin_order_field = 'last_modified'
    was_modified_recently.boolean = True
    was_modified_recently.short_description = 'Modified recently?'

    def state_prov(self):
        phone_pattern = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{4})\D*(\d*)$')
        if phone_pattern.search(self.phone):
            ac = phone_pattern.search(self.phone).groups()[0]
            if ac in AC_DICT:
                return AC_DICT[ac]
        return "UNKNOWN"

    def has_registration_history(self):
        reg_list = None
        reg_history_exists = False
        if self.registrants_set.exists():
            for registrant in self.registrants_set.all():
                if not reg_list:
                    reg_list = registrant.regdetails_set.all()
                else:
                    reg_list = reg_list | registrant.regdetails_set.all()
            if len(reg_list) == 0:
                reg_history_exists = False
            else:
                reg_history_exists = True
        return reg_history_exists
    has_registration_history.boolean = True

    def show_person_url(self):
        return '<a href="%s">%s</a>' % (self.url, self.url)
    show_person_url.allow_tags = True


# OK PER OVERHAUL
class Changes(models.Model):
    """
    Archive of changes/additions/deletions to database
    """
    action = models.CharField(max_length=10)
    orig_id = models.IntegerField()
    name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    phone_main = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    do_not_email = models.BooleanField(default=False)
    do_not_call = models.BooleanField(default=False)
    city = models.CharField(max_length=50, blank=True)
    dept = models.CharField(max_length=50, blank=True, null=True)
    industry = models.TextField(blank=True)  # free-form descripton
    geo = models.CharField(max_length=10, blank=True)
    main_category = models.CharField(max_length=25, blank=True)
    main_category2 = models.CharField(max_length=15, blank=True)
    division1 = models.CharField(max_length=20, blank=True)
    division2 = models.CharField(max_length=20, blank=True)
    date_created = models.DateTimeField('date created')
    created_by = models.ForeignKey('auth.User',
                                   default=1,
                                   related_name='orig_person_created_by')
    date_modified = models.DateTimeField('date modified')
    modified_by = models.ForeignKey('auth.User',
                                    default=1,
                                    related_name='orig_person_modifed_by')


# OK PER OVERHAUL
class Event(models.Model):
    """
    Events being sold/worked on
    """
    number = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    date_begins = models.DateField()
    event_web_site = models.URLField(max_length=255, blank=True, null=True)
    hotel = models.ForeignKey('registration.Venue', blank=True, null=True,
                              on_delete=models.SET_NULL)
    registrar = models.ForeignKey('auth.User', related_name='registrar')
    developer = models.ForeignKey('auth.User', blank=True, null=True,
                                  related_name='developer')
    state_prov = models.CharField(max_length=25,
                                  choices=STATE_PROV_TUPLE)
    company_brand = models.CharField(max_length=2,
                                     choices=COMPANY_OPTIONS,
                                     default='IC')
    gst_charged = models.BooleanField(default=False)
    gst_rate = models.FloatField(default=0.05)
    hst_charged = models.BooleanField(default=True)
    hst_rate = models.FloatField(default=0.13)
    qst_charged = models.BooleanField(default=False)
    qst_rate = models.FloatField(default=0.09975)
    pst_charged = models.BooleanField(default=False)
    pst_rate = models.FloatField(default=0.)
    billing_currency = models.CharField(max_length=3,
                                        choices=BILLING_CURRENCY,
                                        default='CAD')
    created_by = models.ForeignKey('auth.User',
                                   default=1,
                                   related_name='event_created_by')
    date_created = models.DateTimeField('date created', auto_now_add=True)
    date_modified = models.DateTimeField('date modified', auto_now=True)
    modified_by = models.ForeignKey('auth.User',
                                    default=1,
                                    related_name='event_modifed_by')
    default_dept = models.CharField(max_length=50, blank=True, null=True)
    default_cat1 = models.CharField(max_length=25,
                                    choices=CAT_CHOICES,
                                    default='Industry',
                                    blank=True,
                                    null=True)
    default_cat2 = models.CharField(max_length=15,
                                    choices=CAT_CHOICES,
                                    default='NA',
                                    blank=True,
                                    null=True)


    def __str__(self):
        return self.number + ': ' + self.title + ', ' + self.city

    def is_in_past(self):
        return self.start_date < timezone.now().date()


# OK PER OVERHAUL
class EventAssignment(models.Model):
    user = models.ForeignKey('auth.User')
    event = models.ForeignKey(Event)
    role = models.CharField(max_length=2,
                            choices=EVENT_ROLES,
                            default='SA')
    # True means filter; False means start from scratch
    filter_master_selects = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'event',)

    def __str__(self):
        return self.role + ': ' + str(self.user) + ' - ' + str(self.event)


# OK PER OVERHAUL
class Contact(models.Model):
    """
    Records contact history with an individual person
    """
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    event = models.ForeignKey(Event)
    author = models.ForeignKey('auth.User', default=1)
    date_of_contact = models.DateTimeField('date of contact')
    notes = models.TextField()
    method = models.CharField(max_length=20,
                              choices=CONTACT_CHOICES,
                              default='Pitch')

    def __str__(self):
        return str(self.author) + ': ' + self.method + ', ' + \
               str(self.date_of_contact) + \
               self.notes[:20]

    def was_contacted_recently(self):
        return self.date_of_contact >= timezone.now() - \
                                       datetime.timedelta(days=14)

    def able_to_delete(self):
        now = timezone.now()
        return self.date_of_contact >= now - datetime.timedelta(hours=1)


# OK PER OVERHAUL
class DeletedContact(models.Model):
    """
    Archives contact information for deleted persons
    """
    original_pk = models.IntegerField()
    original_person_id = models.IntegerField()
    event = models.ForeignKey(Event)
    author = models.ForeignKey('auth.User', default=1)
    date_of_contact = models.DateTimeField('date of contact')
    notes = models.TextField()
    method = models.CharField(max_length=20)


# NEW - KEEP THIS
class MasterListSelections(models.Model):
    """
    Used to set master territory contact list
    These selects can be refined or ignored on a per-staff member basis
    Does not currently allow selects based on territory splits or individuals
    """
    GEO_CHOICES = (
        ('East', 'East'),
        ('West', 'West'),
        ('Maritimes/East', 'Maritimes'),
        ('USA', 'USA'),
        ('Other', 'Other Foreign'),
        ('Unknown', 'Unknown'),
        ('', '---'),
    )
    CAT_CHOICES = (
        ('HR', 'HR'),
        ('FIN', 'FIN'),
        ('Industry', 'Industry'),
        ('Aboriginal', 'Aboriginal'),
        ('Gov', 'Gov'),
        ('NA', 'None'),
        ('', '---'),
    )
    event = models.ForeignKey(Event)
    geo = models.CharField(max_length=10,
                           choices=GEO_CHOICES,
                           blank=True,
                           default='')
    main_category = models.CharField(max_length=25,
                                     choices=CAT_CHOICES,
                                     blank=True,
                                     default='')  # f1 in original db
    main_category2 = models.CharField(max_length=15,
                                      choices=CAT_CHOICES,
                                      blank=True,
                                      default='')
    company = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    dept = models.CharField(max_length=255, blank=True)
    include_exclude = models.CharField(max_length=7,
                                       choices=(('include', 'include'),
                                                ('exclude', 'exclude')),
                                       default='include')


# Seems good - Keep this
class PersonalListSelections(models.Model):
    GEO_CHOICES = (
        ('East', 'East'),
        ('West', 'West'),
        ('Maritimes/East', 'Maritimes'),
        ('USA', 'USA'),
        ('Other', 'Other Foreign'),
        ('Unknown', 'Unknown'),
        ('', '---'),
    )
    CAT_CHOICES = (
        ('HR', 'HR'),
        ('FIN', 'FIN'),
        ('Industry', 'Industry'),
        ('Aboriginal', 'Aboriginal'),
        ('Gov', 'Gov'),
        ('NA', 'None'),
        ('', '---'),
    )
    DIV_CHOICES = (
        ('1', '1 - Misc'),
        ('2', '2 - Misc'),
        ('3', '3 - Misc'),
        ('4', '4 - Misc'),
        ('5', '5 - Misc'),
        ('6', '6 - Misc'),
        ('A1', '1 - Accounting'),
        ('A2', '2 - Accounting'),
        ('A3', '3 - Accounting'),
        ('Aboriginal', 'Aboriginal'),
        ('FED 1', 'FED 1'),
        ('FED 2', 'FED 2'),
        ('FED 3', 'FED 3'),
        ('FED 4', 'FED 4'),
        ('USA', 'USA'),
        ('NA', 'Not Determined'),
        ('', '---'),
    )
    event_assignment = models.ForeignKey(EventAssignment)
    include_exclude = models.CharField(max_length=7,
                                       choices=(('filter',
                                                 "Filter (exclude values that don't match)"),
                                                ('add', 'Add to List'),
                                                ('exclude', 'Exclude from list'),
                                               ),
                                       default='filter')
    person = models.ForeignKey(Person, blank=True, null=True)
    geo = models.CharField(max_length=10,
                           choices=GEO_CHOICES,
                           blank=True,
                           default='')
    main_category = models.CharField(max_length=25,
                                     choices=CAT_CHOICES,
                                     blank=True,
                                     default='')  # f1 in original db
    main_category2 = models.CharField(max_length=15,
                                      choices=CAT_CHOICES,
                                      blank=True,
                                      default='')
    division1 = models.CharField(max_length=20,
                                 choices=DIV_CHOICES,
                                 blank=True,
                                 default='')  # for splitting leads
    division2 = models.CharField(max_length=20,
                                 choices=DIV_CHOICES,
                                 blank=True,
                                 default='')  # for splitting leads
    company = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    dept = models.CharField(max_length=255, blank=True, null=True)


class Flags(models.Model):
    """
    Flags allowing individual user to id records for followup or action
    """
    event_assignment = models.ForeignKey(EventAssignment,
                                         on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    # flag values:
    #     '1': red
    #     '2': green
    #     '3': blue
    #     '4': black
    #     '5': yellow
    #     '6': purple
    flag = models.CharField(max_length=1, blank=True, default='')
    follow_up_date = models.DateField(blank=True, null=True)

    class Meta:
        unique_together=('event_assignment', 'person')
