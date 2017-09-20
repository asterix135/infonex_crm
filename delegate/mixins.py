import re

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone

from crm.mixins import ChangeRecord
from delegate.constants import NON_INVOICE_VALUES
from delegate.forms import AssistantForm, CompanySelectForm, NewDelegateForm, \
        RegDetailsForm
from registration.models import Assistant, Invoice, RegDetails, RegEventOptions

class Substitution():

    def process_substitution(self, request):
        original_registrant = self.current_registration.registrant
        self.current_registration.registrant = self.registrant
        self.current_registration.save()
        substitute_reg_record = RegDetails(
            conference = self.current_registration.conference,
            registrant = original_registrant,
            register_date = self.current_registration.register_date,
            cancellation_date = self.current_registration.cancellation_date,
            registration_status = 'B',
            registration_notes = self.current_registration.registration_notes,
            created_by = request.user,
            date_created = timezone.now(),
            modified_by = request.user,
            date_modified = timezone.now(),
        )
        substitute_reg_record.save()


class ProcessCompleteRegistration(Substitution, ChangeRecord):

    def _set_original_registrant(self, request):
        if self.current_registration and request.POST['action_type'] == 'sub':
            self.original_registrant = self.current_registration.registrant
            self.reg_details_form.data['revised_flag'] = True

    def _set_session_params(self, request):
        request.session['current_registration'] = self.current_registration.pk
        request.session['registrant'] = self.registrant.pk
        if self.assistant:
            request.session['assistant'] = self.assistant.pk
        else:
            request.session['assistant'] = None
        request.session['reg_action'] = request.POST['action_type']

    def _update_assistant(self, request):
        if request.POST['assistant_match_value']:
            self.assistant = Assistant.objects.get(
                pk=request.POST['assistant_match_value']
            )
            # form has to be reinstantiated with instance
            self.assistant_form = AssistantForm(
                self.assistant_form.data, instance=self.assistant
            )
            self.assistant_form.save()
        elif self.has_assistant_data:
            self.assistant = self.assistant_form.save()
        else:
            self.assistant = None

    def _update_company(self, request):
        # form has to be reinstantiated with instance
        self.company_select_form = CompanySelectForm(
            self.company_select_form.data,
            instance=self.company
        )
        self.company_select_form.save()

    def _update_crm(self, request):
        self.crm_match.name = \
                self.new_delegate_form.cleaned_data['first_name'] + ' ' + \
                self.new_delegate_form.cleaned_data['last_name']
        self.crm_match.title = self.new_delegate_form.cleaned_data['title']
        if self.company_select_form.cleaned_data['name'] not in ('', None):
            self.crm_match.company = \
                    self.company_select_form.cleaned_data['name']
        else:
            self.crm_match.company = self.crm_match.name
        self.crm_match.phone = self.new_delegate_form.cleaned_data['phone1']
        self.crm_match.phone_alternate = \
                self.new_delegate_form.cleaned_data['phone2']
        self.crm_match.email = self.new_delegate_form.cleaned_data['email1']
        self.crm_match.email_alternate = \
                self.new_delegate_form.cleaned_data['email2']
        self.crm_match.city = self.company_select_form.cleaned_data['city']
        self.crm_match.date_modified = timezone.now()
        self.crm_match.modified_by = request.user
        if not self.crm_match.dept:
            self.crm_match.dept = self.conference.default_dept
        self.crm_match.save()
        self.add_change_record(self.crm_match, 'update')

    def _update_database_records(self, request):
        self._update_assistant(request)
        self._update_company(request)
        self._update_crm(request)
        self._update_registrant(request)
        self._update_reg_details(request)
        self._update_invoice(request)
        self._update_event_options(request)

    def _update_event_options(self, request):
        if len(self.option_list) > 0:
            for option in self.option_list:
                if not RegEventOptions.objects.filter(
                    reg=self.current_registration,
                    option=option
                ).exists():
                    new_option = RegEventOptions(
                        reg=self.current_registration,
                        option=option
                    )
                    new_option.save()

    def _update_invoice(self, request):
        try:
            current_invoice = Invoice.objects.get(
                reg_details = self.current_registration
            )
        except Invoice.DoesNotExist:
            if self.current_registration.registration_status in \
                    NON_INVOICE_VALUES:
                current_invoice = None
            else:
                current_invoice = Invoice(
                    reg_details=self.current_registration,
                )
        if current_invoice:
            # form has to be reinstantiated with instance
            self.reg_details_form = RegDetailsForm(
                self.reg_details_form.data, instance=current_invoice
            )
            self.reg_details_form.save()

    def _update_registrant(self, request):
        if self.registrant:
            # form has to be reinstantiated with instance
            self.new_delegate_form = NewDelegateForm(
                self.new_delegate_form.data,
                instance = self.registrant
            )
            self.new_delegate_form.save()
        else:
            self.registrant = self.new_delegate_form.save(commit=False)
            self.registrant.crm_person = self.crm_match
            self.registrant.company = self.company
            self.registrant.created_by = request.user
            self.registrant.date_created = timezone.now()
        self.registrant.assistant = self.assistant
        self.registrant.modified_by = request.user
        self.registrant.date_modified = timezone.now()
        self.registrant.save()

    def _update_reg_details(self, request):
        if not self.current_registration:
            reg_detail_db_check = RegDetails.objects.filter(
                conference=self.conference,
                registrant=self.registrant
            )
            if reg_detail_db_check.count() > 0 and \
                    reg_detail_db_check[0].registration_status \
                    not in ('SP', 'SU'):
                self.current_registration = reg_detail_db_check[0]
            else:
                self.current_registration = RegDetails(
                    date_created=timezone.now(),
                    created_by=request.user
                )
            self.current_registration.conference = self.conference
            self.current_registration.registrant = self.registrant
        elif self.conference != self.current_registration.conference:
            raise ValueError('\nConference changed for registration\n')
        elif request.POST['action_type'] == 'sub':
            self.process_substitution(request)

        self.current_registration.register_date = \
                self.reg_details_form.cleaned_data['register_date']
        if self.reg_details_form.cleaned_data['cancellation_date']:
            self.current_registration.cancellation_date = \
                    self.reg_details_form.cleaned_data['cancellation_date']
        else:
            self.current_registration.cancellation_date = None
        self.current_registration.registration_status = \
                self.reg_details_form.cleaned_data['registration_status']
        self.current_registration.registration_notes = \
                self.reg_details_form.cleaned_data['registration_notes']
        self.current_registration.modified_by = request.user
        self.current_registration.date_modified = timezone.now()
        self.current_registration.save()

    def process_complete_registration(self, request):
        self._set_original_registrant(request)
        self._update_database_records(request)

        self._set_session_params(request)


class PdfResponseMixin():
    pdf_name = 'output'

    def get_pdf_name(self):
        return self.pdf_name

    def render_to_response(self, context, **response_kwargs):
        try:
            pdf = response_kwargs.pop('pdf')
        except KeyError:
            pdf = context.pop('pdf', None)
        response = HttpResponse(content_type='application/pdf')
        file_details = 'inline; filename="{0}.pdf"'.format(self.get_pdf_name())
        response.write(pdf)
        return response
