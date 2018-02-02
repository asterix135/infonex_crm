"""
functions related to processing & sending mass mail to delegates
"""

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
import os
import time

from registration.models import RegDetails, EventOptions
from infonex_crm.settings import BASE_DIR


class MassMail():
    def __init__(self, subject, message, msg_type, post_data, event=None):
        self._subject = subject
        self._message = message
        self._recipients = self._build_mail_dict(post_data)
        self._msg_type = msg_type
        self._password_dict = {}
        if event:
            self.set_event(event)

    def _build_mail_dict(self, post_data):
        """
        builds dict for sending email:
        key: regdetails.pk (or N + sequence number)
        value: dict: {'email': email, 'salutation': salutation}
        """
        email_dict = {}
        for key in post_data:
            if key[:7] == 'address':
                row_id = key.partition('_')[2]
                if row_id in email_dict:
                    email_dict[row_id]['email'] = post_data[key]
                else:
                    email_dict[row_id] = {'email': post_data[key],
                                          'salutation': None,}
            elif key[:7] == 'salutat':
                row_id = key.partition('_')[2]
                if row_id in email_dict:
                    email_dict[row_id]['salutation'] = post_data[key]
                else:
                    email_dict[row_id] = {'email': None,
                                          'salutation': post_data[key],}
        return email_dict

    def _append_to_pw_text(self, regeventoption_obj, pw_text):

        addl_text = 'USER NAME: ' + 'foo'

    def _insert_passwords(self, msg_body, reg_detail_id):
        password_text = ''
        try:
            reg_details = RegDetails.objects.get(pk=reg_detail_id)
            if reg_details.regeventoptions_set.exists():
                options_set = reg_details.regeventoptions_set.all()
            else:
                options_set = None
        except (ValueError, RegDetails.DoesNotExist):
            options_set = None

        # if no options set for event, only return
        if not self._default_options:
            password_text = 'USERNAME: ' + \
                self._password_dict['all']['username'] + \
                '<br/>PASSWORD: ' + \
                self._password_dict['all']['password'] + '<br/><br/>'
        elif not options_set:
            event_defaults = self._event.eventoptions_set.filter(primary=True)
            for option in event_defaults:
                password_text += '<em>' + option.name + '</em><br/>' + \
                    'USERNAME: ' + \
                    self._password_dict[str(option.pk)]['username'] + \
                    '<br/>PASSWORD: ' + \
                    self._password_dict[str(option.pk)]['password'] + \
                    '<br/><br/>'
        else:
            for option in options_set:
                password_text += '<em>' + option.option.name + '</em><br/>' + \
                    'USERNAME: ' + \
                    self._password_dict[str(option.option.pk)]['username'] + \
                    '<br/>PASSWORD: ' + \
                    self._password_dict[str(option.option.pk)]['password'] + \
                    '<br/><br>'
        msg_body = msg_body.replace(
            '**!!DO NOT CHANGE THIS LINE!!**',
            password_text[:-5]  # Remove final <br/>
        )
        return msg_body

    def set_subject(self, subject_text):
        self._subject = subject_text

    def set_message(self, message_text):
        self._message = message_text

    def set_event(self, event_object):
        self._event = event_object
        try:
            self._default_options = self._event.eventoptions_set.all()
        except EventOptions.DoesNotExist:
            self._default_options = None

    def set_passwords(self, post_data):
        password_dict = {}
        for key in post_data:
            if key[:8] == 'username':
                option_id = key.partition('_')[2]
                if option_id in password_dict:
                    password_dict[option_id]['username'] = post_data[key]
                else:
                    password_dict[option_id] = {'username': post_data[key],
                                                'password': None}
            elif key[:8] == 'password':
                option_id = key.partition('_')[2]
                if option_id in password_dict:
                    password_dict[option_id]['password'] = post_data[key]
                else:
                    password_dict[option_id] = {'username': None,
                                                'password': post_data[key]}
        self._password_dict = password_dict

    def send_mail(self):
        # need to ensure address is minimally valid email
        sent_emails = ['', None]
        with open(os.path.join(
            BASE_DIR,
            'registration/static/registration/email_text/genericbanner.png'
        ), 'rb') as fp:
            image1 = MIMEImage(fp.read())
        image1.add_header('Content-ID', '<{}>'.format('image1'))
        for key in self._recipients:
            reg_id = key
            address = self._recipients[key]['email']
            salutation = self._recipients[key]['salutation']
            email_body = self._message
            if address not in sent_emails:
                if salutation not in ('', None):
                    email_body = 'Dear ' + salutation + ':<br/><br/>' + \
                        self._message
                if self._msg_type in ('docs', 'thanks'):
                    email_body = self._insert_passwords(email_body, key)
                email_body = '<img src="cid:image1" style="width:auto; max-width:100%;"/><br/><br/>' + email_body
                email = EmailMessage(
                    subject = self._subject,
                    body = email_body,
                    to = [address]
                )
                email.content_subtype = 'html'
                email.mixed_subtype = 'related'
                email.attach(image1)
                email.send()
                sent_emails.append(address)
                time.sleep(0.5)
