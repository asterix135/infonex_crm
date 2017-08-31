from django.db import models

from registration.constants import STATE_PROV_TUPLE, REG_STATUS_OPTIONS, \
    PAYMENT_METHODS

class QueuedOrders(models.Model):
    date_created = models.DateTimeField('date created', auto_now_add=True)
    # fields for Registrant table
    salutation = models.CharField(max_length=15, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True, null=True)
    email1 = models.EmailField(blank=True, null=True)
    email2 = models.EmailField(blank=True, null=True)
    phone1 = models.CharField(max_length=25, blank=True, null=True)
    phone2 = models.CharField(max_length=25, blank=True, null=True)
    # fields for Company table
    company_name = models.CharField(max_length=255, blank=True, null=True)
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state_prov = models.CharField(max_length=25, blank=True, null=True,
                                  choices=STATE_PROV_TUPLE)
    postal_code = models.CharField(max_length=25, blank=True, null=True)
    country = models.CharField(max_length=25, blank=True, null=True)
    # fields for RegDetails table
    conference = models.ForeignKey('crm.Event', on_delete=models.CASCADE)
    registration_status=models.CharField(max_length=2,
                                         choices=REG_STATUS_OPTIONS,
                                         default='DU')
    registration_notes=models.TextField(blank=True, null=True)
    # fields for Invoice table
    sales_credit = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                     blank=True, null=True)
    pre_tax_price = models.DecimalField(max_digits=10, decimal_places=2,
                                        null=True, blank=True)
    gst_rate = models.DecimalField(max_digits=6, decimal_places=5, default=0.05,
                                   blank=True, null=True)
    hst_rate = models.DecimalField(max_digits=6, decimal_places=5, default=0.13,
                                   blank=True, null=True)
    qst_rate = models.DecimalField(max_digits=6, decimal_places=5,
                                   default=0.09975, blank=True, null=True)
    payment_method = models.CharField(max_length=1,
                                      choices=PAYMENT_METHODS,
                                      blank=True,
                                      null=True)
    invoice_notes = models.TextField(blank=True, null=True)
    # fields for Assistant
    asst_salutation = models.CharField(max_length=15, blank=True, null=True)
    asst_first_name = models.CharField(max_length=100, blank=True, null=True)
    asst_last_name = models.CharField(max_length=100, blank=True, null=True)
    asst_title = models.CharField(max_length=100, blank=True, null=True)
    asst_email = models.EmailField(blank=True, null=True)
    asst_phone = models.CharField(max_length=25, blank=True, null=True)
