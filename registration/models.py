import datetime

from django.db import models
from django.utils import timezone

from .constants import *


class Assistant(models.Model):
    """
    Details on person/people to receive copy of invoice (cc or attn:)
    """
    salutation = models.CharField(max_length=15, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=40, blank=True, null=True)
    address_personal = models.CharField(max_length=255, blank=True, null=True)


class Company(models.Model):
    """
    Company Details
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    name_for_badges = models.CharField(max_length=30, blank=True, null=True)
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state_prov = models.CharField(max_length=25, blank=True, null=True,
                                  choices=STATE_PROV_TUPLE)
    postal_code = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=25, blank=True, null=True)
    gst_hst_exempt = models.BooleanField(default=False)
    qst_exempt = models.BooleanField(default=False)
    gst_hst_exemption_number = models.CharField(max_length=25,
                                                blank=True, null=True)
    qst_exemption_number = models.CharField(max_length=25,
                                            blank=True, null=True)


class Registrants(models.Model):
    """
    Personal (not company) information for Event Attendees
    """
    crm_person = models.ForeignKey('crm.Person', blank=True, null=True,
                                   on_delete=models.SET_NULL)
    assistant = models.ForeignKey(Assistant, blank=True, null=True,
                                  on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    salutation = models.CharField(max_length=15, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True, null=True)
    email1 = models.EmailField(blank=True, null=True)
    email2 = models.EmailField(blank=True, null=True)
    phone1 = models.CharField(max_length=40, blank=True, null=True)
    phone2 = models.CharField(max_length=40, blank=True, null=True)
    contact_option = models.CharField(max_length=1,
                               choices=CONTACT_OPTIONS,
                               default='D')
    delegate_notes = models.TextField(blank=True, null=True)
    speaker_bio = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('auth.User',
                                   default=1,
                                   related_name='del_created_by',
                                   on_delete=models.SET_DEFAULT)
    date_created = models.DateTimeField('date created', auto_now_add=True)
    date_modified = models.DateTimeField('date modified', auto_now=True)
    modified_by = models.ForeignKey('auth.User',
                                    default=1,
                                    related_name='del_modifed_by',
                                    on_delete=models.SET_DEFAULT)

    def __str__(self):
        return(self.first_name + ' ' + self.last_name + ', ' + self.company.name)

    def clean(self):
        """
        Cleans white space from CharFields and TextFields
        """
        for field in self._meta.fields:
            if isinstance(field, (models.CharField, models.TextField)):
                value = getattr(self, field.name)
                if value:
                    setattr(self, field.name, value.strip())


class RegDetails(models.Model):
    """
    contains details on booking for invoicing & event management
    """
    conference = models.ForeignKey('crm.Event',
                                   on_delete=models.CASCADE)
    registrant = models.ForeignKey(Registrants,
                                   on_delete=models.CASCADE)
    register_date = models.DateField(default=timezone.now)
    cancellation_date = models.DateField(blank=True, null=True)
    registration_status = models.CharField(max_length=2,
                                           choices=REG_STATUS_OPTIONS,
                                           default='DU')
    registration_notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('auth.User',
                                   default=1,
                                   related_name='reg_created_by',
                                   on_delete=models.SET_DEFAULT)
    date_created = models.DateTimeField('date created', auto_now_add=True)
    date_modified = models.DateTimeField('date modified', auto_now=True)
    modified_by = models.ForeignKey('auth.User',
                                    default=1,
                                    related_name='reg_modifed_by',
                                    on_delete=models.SET_DEFAULT)


class Invoice(models.Model):
    """
    Holds invoice details for paying Registrants
    """
    reg_details = models.OneToOneField(
        RegDetails,
        on_delete=models.CASCADE,
    )
    sales_credit = models.ForeignKey('auth.User',
                                     related_name='sales_credit',
                                     default=1,
                                     blank=True,
                                     on_delete=models.SET_DEFAULT)
    pre_tax_price = models.DecimalField(max_digits=10, decimal_places=2,
                                        null=True, blank=True)
    gst_rate = models.DecimalField(max_digits=6, decimal_places=5, default=0.05,
                                   blank=True, null=True)
    hst_rate = models.DecimalField(max_digits=6, decimal_places=5, default=0.13,
                                   blank=True, null=True)
    qst_rate = models.DecimalField(max_digits=6, decimal_places=5,
                                   default=0.09975, blank=True, null=True)
    pst_rate = models.DecimalField(max_digits=6, decimal_places=5, default=0)
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.CharField(max_length=1,
                                      choices=PAYMENT_METHODS,
                                      blank=True,
                                      null=True)
    fx_conversion_rate = models.DecimalField(max_digits=10, decimal_places=6,
                                             default=1.0)
    invoice_notes = models.TextField(blank=True, null=True)
    sponsorship_description = models.TextField(blank=True, null=True)
    revised_flag = models.BooleanField(default=False)


class Venue(models.Model):
    """
    List of Venues with Details
    """
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state_prov = models.CharField(max_length=25)
    postal_code = models.CharField(max_length=25)
    phone = models.CharField(max_length=25)
    hotel_url = models.URLField()

    def __str__(self):
        return str(self.name) + ' (' + str(self.city) + ')'


class EventOptions(models.Model):
    """
    Contains details on different bookable sections of a particular event
    """
    event = models.ForeignKey('crm.Event', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    startdate = models.DateField()
    enddate = models.DateField()
    primary = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return(self.name + ': ' + str(self.startdate) + ' - ' +
               str(self.enddate))


class RegEventOptions(models.Model):
    """
    Contains details on what event options a person is registered for
    """
    reg = models.ForeignKey(RegDetails, on_delete=models.CASCADE)
    option = models.ForeignKey(EventOptions, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('reg', 'option')
