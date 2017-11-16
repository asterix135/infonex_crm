import re

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone

from crm.mixins import ChangeRecord
from delegate.constants import NON_INVOICE_VALUES, STOPWORDS, \
        SEARCH_SUBSTITUTIONS
from delegate.forms import AssistantForm, CompanySelectForm, NewDelegateForm, \
        RegDetailsForm
from registration.models import Assistant, Company, Invoice, RegDetails, \
        RegEventOptions

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


class GuessCompanyMixin():

    def _get_match_1(self, company_name, postal_code, city, search_by_name_first):
        if search_by_name_first and postal_code in ('', None) and \
                city in ('', None):
            return Company.objects.filter(name__iexact=company_name)
        if search_by_name_first and city not in ('', None):
            return Company.objects.filter(name__iexact=company_name,
                                          city__iexact=city)
        return Company.objects.filter(name__iexact=company_name,
                                      city__iexact=city)

    def _get_match_2(self, company_name, search_by_name_first, city, postal_code):
        match2 = self._iteratively_replace_and_guess_name(company_name)
        if search_by_name_first and city not in ('', None):
            return match2.filter(city__icontains=city)
        if postal_code not in ('', None) or not search_by_name_first:
            return match2.filter(postal_code__iexact=postal_code)
        return match2

    def _get_weaker_matches(self, company_name, search_by_name_first, city,
                            postal_code, match1, match2):
        # check for companies containing name as is
        match3 = Company.objects.filter(name__icontains=company_name)
        if match3.count() > 0:
            match3 = match3.exclude(id__in=match1).exclude(id__in=match2)
            ordered_list = self._order_list_by_registrants(match3)
            self.company_suggest_list.extend(list(ordered_list))
        # set up stuff for subsequent searches
        if search_by_name_first and postal_code in ('', None):
            match_base = Company.objects.all()
        else:
            match_base = Company.objects.filter(postal_code=postal_code)
        match4 = Company.objects.none()
        match5 = Company.objects.none()
        # first try trigrams
        if len(company_name.split()) > 3 and len(self.company_suggest_list) < 15:
            queries = []
            trigram_list = zip(company_name.split(),
                               company_name.split()[1:],
                               company_name.split()[2:])
            for trigram in trigram_list:
                if trigram[0] not in STOPWORDS or trigram[1] not in STOPWORDS \
                    or trigram[2] not in STOPWORDS:
                    search_term = ' '.join(trigram)
                    queries.append(Q(name__icontains=search_term))
            if len(queries) > 0:
                query = queries.pop()
                for item in queries:
                    query |= item
                match4 = match_base.filter(query)
                match4 = match4.exclude(id__in=match1).exclude(id__in=match2). \
                    exclude(id__in=match3)
                ordered_list = self._order_list_by_registrants(match4)
                self.company_suggest_list.extend(list(
                    ordered_list[:15-len(self.company_suggest_list)]
                ))

        # next try bigrams
        if len(company_name.split()) > 2 and len(self.company_suggest_list) < 15:
            queries = []
            bigram_list = zip(company_name.split(),
                              company_name.split()[1:])
            for bigram in bigram_list:
                if bigram[0] not in STOPWORDS or bigram[1] not in STOPWORDS:
                    search_term = ' '.join(bigram)
                    queries.append(Q(name__icontains=search_term))
            if len(queries) > 0:
                query = queries.pop()
                for item in queries:
                    query |= item
                match5 = match_base.filter(query)
                match5 = match5.exclude(id__in=match1).exclude(id__in=match2). \
                    exclude(id__in=match3).exclude(id__in=match4)
                ordered_list = self._order_list_by_registrants(match5)
                self.company_suggest_list.extend(list(
                    ordered_list[:15-len(self.company_suggest_list)]
                ))

        # finally try keywords
        if len(self.company_suggest_list) < 15:
            queries = []
            name_tokens = [x for x in company_name.split() if x not in STOPWORDS]
            for token in name_tokens:
                queries.append(Q(name__icontains=token))
            if len(queries) > 0:
                query = queries.pop()
                for item in queries:
                    query |= item
                match6 = match_base.filter(query)
                match6 = match6.exclude(id__in=match1).exclude(id__in=match2). \
                    exclude(id__in=match3).exclude(id__in=match4). \
                    exclude(id__in=match5)
                ordered_list = self._order_list_by_registrants(match6)
                self.company_suggest_list.extend(list(
                    ordered_list[:15-len(self.company_suggest_list)]
                ))

    def _iteratively_replace_and_guess_name(self, company_name):
        alternate_names = []
        name_with_all_replacements1 = company_name
        name_with_all_replacements2 = company_name
        for substitution in SEARCH_SUBSTITUTIONS:
            regex1 = re.compile(r'\b' + substitution[0].lower() + r'\b')
            regex2 = re.compile(r'\b' + substitution[1].lower() + r'\b')
            if regex1.search(company_name):
                alternate_names.append(
                    regex1.sub(substitution[1], company_name)
                )
                name_with_all_replacements1 = regex1.sub(
                    substitution[1], name_with_all_replacements1
                )
            if regex2.search(company_name):
                alternate_names.append(
                    regex2.sub(substitution[0], company_name)
                )
                name_with_all_replacements2 = regex2.sub(
                    substitution[0], name_with_all_replacements2
                )
        if name_with_all_replacements1 != company_name:
            alternate_names.append(name_with_all_replacements1)
        if name_with_all_replacements2 != company_name:
            alternate_names.append(name_with_all_replacements2)
        queries = []
        for name in alternate_names:
            if len(name) > 2:
                queries.append(Q(name__icontains=name))
            else:
                queries.append(Q(name__iexact=name))
        if len(queries) > 0:
            query = queries.pop()
            for item in queries:
                query |= item
            return Company.objects.filter(query)
        return Company.objects.none()

    def _order_list_by_registrants(self, queryset):
        return queryset.annotate(
            num_customers=Count('registrants')
        ).order_by('-num_customers')

    def guess_company(self, request, search_by_name_first=False):
        """
        Returns company_best_guess and sets self.company_suggest_list
        """
        # Set empty variables to be returned if nothing found or added
        company_best_guess = None
        self.company_suggest_list = []
        # skip all this if we have a company match
        if self.company:
            return company_best_guess

        # Extract search data from request.GET
        company_name = ' '.join(request.GET['company_name'].lower().strip().split())
        address1 = request.GET['address1']
        city = request.GET['city']
        postal_code = request.GET['postal_code']

        # get most likely best match and - if exists - update reutrn variables
        match1 = self._get_match_1(company_name, postal_code,
                                   city, search_by_name_first)
        if match1.count() > 0:
            ordered_list = self._order_list_by_registrants(match1)
            company_best_guess = ordered_list[0]
            self.company_suggest_list.extend(list(ordered_list))

        # check alternate names/spellings
        match2 = self._get_match_2(company_name, search_by_name_first,
                                   city, postal_code)
        if match2.count() > 0:
            ordered_list = self._order_list_by_registrants(match2)
            if not company_best_guess:
                company_best_guess = ordered_list[0]
            self.company_suggest_list.extend(list(ordered_list))

        # following searches only update self.company_suggest_list
        # they aren't reliable to update company_best_guess
        if len(self.company_suggest_list) < 15:
            self._get_weaker_matches(company_name, search_by_name_first,
                                     city, postal_code, match1, match2)
        return company_best_guess
