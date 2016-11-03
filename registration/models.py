import datetime
from django.db import models
from .constants import PAYMENT_METHODS, REG_STATUS_OPTIONS, CONTACT_OPTIONS


class Assistant(models.Model):
    """
    Details on person/people to receive copy of invoice (cc or attn:)
    """
    salutation = models.CharField(max_length=15, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=25, blank=True)
    address_personal = models.CharField(max_length=255, blank=True)


class Company(models.Model):
    """
    Company Details
    """
    name = models.CharField(max_length=255, blank=True)
    name_for_badges = models.CharField(max_length=30, blank=True)
    address1 = models.CharField(max_length=255, blank=True)
    address2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_prov = models.CharField(max_length=25, blank=True)
    postal_code = models.CharField(max_length=15, blank=True)
    country = models.CharField(max_length=25, blank=True)
    gst_hst_exempt = models.BooleanField(default=False)
    qst_exempt = models.BooleanField(default=False)
    gst_hst_exemption_number = models.CharField(max_length=25)
    qst_exemption_number = models.CharField(max_length=25)


class Registrants(models.Model):
    """
    Personal (not company) information for Event Attendees
    """
    crm_contact = models.ForeignKey('crm.Contact', blank=True)
    assistant = models.ForeignKey(Assistant, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    salutation = models.CharField(max_length=15, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    email1 = models.EmailField(blank=True)
    email2 = models.EmailField(blank=True)
    phone1 = models.CharField(max_length=25, blank=True)
    phone2 = models.CharField(max_length=25, blank=True)
    contact_option = models.CharField(max_length=1,
                               choices=CONTACT_OPTIONS,
                               default='D')
    delegate_notes = models.TextField(blank=True)
    speaker_bio = models.TextField(blank=True)
    created_by = models.ForeignKey('auth.User',
                                   default=1,
                                   related_name='del_created_by')
    date_created = models.DateTimeField('date created', auto_now_add=True)
    date_modified = models.DateTimeField('date modified', auto_now=True)
    modified_by = models.ForeignKey('auth.User',
                                    default=1,
                                    related_name='del_modifed_by')


class RegDetails(models.Model):
    """
    contains details on booking for invoicing & event management
    """
    invoice_number = models.IntegerField(unique=True)
    conference = models.ForeignKey('crm.Event')
    registrant = models.ForeignKey(Registrants)
    priority_code = models.CharField(max_length=25)
    sales_credit = models.CharField(max_length=50)
    pre_tax_price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=6, decimal_places=5)
    hst_rate = models.DecimalField(max_digits=6, decimal_places=5)
    qst_rate = models.DecimalField(max_digits=6, decimal_places=5)
    pst_rate = models.DecimalField(max_digits=6, decimal_places=5)
    payment_date = models.DateField(blank=True)
    payment_method = models.CharField(max_length=1,
                                      choices=PAYMENT_METHODS,
                                      blank=True,
                                      default=False)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_date = models.DateField(blank=True)
    depost_method = models.CharField(max_length=1,
                                     choices=PAYMENT_METHODS,
                                     blank=True,
                                     default=False)
    fx_conversion_rate = models.DecimalField(max_digits=10, decimal_places=6)
    register_date = models.DateField(default=datetime.date.today)
    cancellation_date = models.DateField(blank=True)
    # Consider how to handle options: maybe different from current db?
    registration_status = models.CharField(max_length=2,
                                           choices=REG_STATUS_OPTIONS,
                                           default='DU')
    invoice_notes = models.TextField(blank=True)
    registration_notes = models.TextField(blank=True)
    sponsorship_description = models.TextField(blank=True)
    created_by = models.ForeignKey('auth.User',
                                   default=1,
                                   related_name='reg_created_by')
    date_created = models.DateTimeField('date created', auto_now_add=True)
    date_modified = models.DateTimeField('date modified', auto_now=True)
    modified_by = models.ForeignKey('auth.User',
                                    default=1,
                                    related_name='reg_modifed_by')
