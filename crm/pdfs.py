from datetime import datetime
from io import BytesIO
import os

from delegate.constants import NON_INVOICE_VALUES
from registration.constants import REG_STATUS_OPTIONS
from registration.models import EventOptions
from infonex_crm.settings import BASE_DIR

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, mm, cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

LOGO_PATH = os.path.join(
    BASE_DIR,
    'delegate/static/delegate/INFONEX-logo-tag.jpg'
)
PAGE_HEIGHT = letter[1]
PAGE_WIDTH = letter[0]

class RegFormPdf:
    """
    Generate pdf reg form for a specific crm contact
    """

    def __init__(self, conf_obj, user, reg_details, start_posn=None):
        self.event = conf_obj
        self.user = user
        self.details = reg_details
        self.start_posn = start_posn if start_posn else PAGE_HEIGHT-inch

    def _calculate_tax_total(self, price):
        try:
            gst_rate = float(self.details['gst_rate'])
        except ValueError:
            gst_rate = self.event.gst_rate
        try:
            hst_rate = float(self.details['hst_rate'])
        except ValueError:
            hst_rate = self.event.hst_rate
        try:
            qst_rate = float(self.details['qst_rate'])
        except ValueError:
            qst_rate = self.event.qst_rate
        gst = price * self.event.gst_charged * gst_rate
        hst = price * self.event.hst_charged * hst_rate
        qst = price * self.event.qst_charged * qst_rate
        inv_total = price + gst + hst + qst
        return '${:0,.2f}'.format(gst), '${:0,.2f}'.format(hst), \
               '${:0,.2f}'.format(qst), '${:0,.2f}'.format(inv_total)

    def _add_page_outline(self, canvas):
        start_posn = self.start_posn
        canvas.setLineWidth(2)
        canvas.rect(cm, cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-2*cm)
        canvas.drawImage(LOGO_PATH, 0.5*inch, start_posn,
                       height=0.5*inch, width=1.875*inch)
        canvas.setFont('Helvetica-Bold', 24)
        canvas.drawRightString(PAGE_WIDTH-(0.5*inch), start_posn + 0.15*inch,
                               'REGISTRATION FORM')
        footer_text = 'This form created on '
        footer_text += datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(PAGE_WIDTH-(0.5*inch), 0.5*inch, footer_text)
        self.start_posn = start_posn - 0.4 * inch
        sales_rep_text = 'BOOKING REP: '
        if self.user.first_name or self.user.last_name:
            sales_rep_text += self.user.first_name + ' ' + self.user.last_name
        else:
            sales_rep_text += self.user.username
        canvas.setFont('Helvetica-Bold', 9.5)
        canvas.drawString(0.5*inch, 0.5*inch, sales_rep_text)

    def _add_conference_details(self, canvas):
        start_posn = self.start_posn
        canvas.setFillColor(colors.blue)
        canvas.setFont('Helvetica', 10)
        canvas.drawString(0.5*inch, start_posn,
                          'Section A - Conference Information')
        canvas.setFillColor(colors.black)
        canvas.setLineWidth(1)
        canvas.rect(0.5*inch, start_posn - 0.4*inch,
                    PAGE_WIDTH-inch, 0.3*inch)
        canvas.line(2.5*inch, start_posn - 0.4*inch,
                    2.5*inch, start_posn - 0.1*inch)
        canvas.setFillColor(colors.red)
        canvas.drawString(0.7*inch, start_posn-0.3*inch,
                          self.event.number)
        canvas.setFillColor(colors.black)
        canvas.drawString(2.7*inch, start_posn-0.3*inch,
                          self.event.title)
        self.start_posn = start_posn - 0.65 * inch

    def _add_event_options(self, canvas):
        start_posn = self.start_posn
        num_options = len(self.details['event_options'])
        canvas.setFont('Helvetica', 10)
        canvas.setLineWidth(1)
        canvas.setFillColor(colors.blue)
        canvas.drawString(0.5*inch, start_posn,
                          'Conference Options Selected')
        canvas.setFillColor(colors.black)
        canvas.rect(0.5*inch, start_posn-(0.1+num_options*0.3)*inch,
                    PAGE_WIDTH-inch, num_options*0.3*inch)
        option_start = start_posn - 0.3 * inch
        for option in self.details['event_options']:
            event_option = EventOptions.objects.get(pk=option)
            option_text = event_option.name + ':  '
            option_text += event_option.startdate.strftime('%-d %B, %Y')
            if event_option.enddate != event_option.startdate:
                option_text += ' to '
                option_text += event_option.enddate.strftime('%-d %B, %Y')
            canvas.drawString(0.7 * inch, option_start, option_text)
            canvas.line(0.5*inch, option_start-(0.1*inch),
                        PAGE_WIDTH-0.5*inch, option_start-(0.1*inch))
            option_start -= 0.3 * inch
        self.start_posn = option_start - 0.05 * inch

    def _add_delegate_information(self, canvas):
        start_posn = self.start_posn
        canvas.setFillColor(colors.blue)
        canvas.setFont('Helvetica', 10)
        canvas.drawString(0.5*inch, start_posn,
                          'Section B - Delegate Information')
        canvas.setLineWidth(1)
        canvas.setFillColor(colors.black)
        canvas.rect(0.5*inch, start_posn-1.3*inch,
                    PAGE_WIDTH-inch, 1.2*inch)
        canvas.line(2.5*inch, start_posn-1.3*inch,
                    2.5*inch, start_posn-0.1*inch)
        canvas.drawString(0.7 * inch, start_posn-0.3*inch, 'Delegate Name:')
        name = ''
        if self.details['salutation'].strip() != '':
            name += self.details['salutation'].strip() + ' '
        if self.details['first_name'].strip != '':
            name += self.details['first_name'].strip() + ' '
        name += self.details['last_name'].strip()
        canvas.drawString(2.7 * inch, start_posn-0.3*inch, name)
        canvas.line(0.5*inch, start_posn-0.4*inch,
                    PAGE_WIDTH-0.5*inch, start_posn-0.4*inch)
        canvas.drawString(0.7*inch, start_posn-0.6*inch, 'Delegate Title:')
        canvas.drawString(2.7*inch, start_posn-0.6*inch,
                          self.details['title'].strip())
        canvas.line(0.5*inch, start_posn-0.7*inch,
                    PAGE_WIDTH-0.5*inch, start_posn-0.7*inch)
        canvas.drawString(0.7*inch, start_posn-0.9*inch, 'Email:')
        canvas.drawString(2.7*inch, start_posn-0.9*inch,
                          self.details['email1'].strip())
        canvas.line(0.5*inch, start_posn-1.0*inch,
                    PAGE_WIDTH-0.5*inch, start_posn-1.0*inch)
        canvas.drawString(0.7*inch, start_posn-1.2*inch, 'Phone:')
        canvas.drawString(2.7*inch, start_posn-1.2*inch,
                          self.details['phone1'].strip())
        self.start_posn = start_posn-1.55*inch

    def _add_company_information(self, canvas):
        start_posn = self.start_posn
        canvas.setFillColor(colors.blue)
        canvas.setFont('Helvetica', 10)
        canvas.drawString(0.5*inch, start_posn,
                          'Section C: Company Information')
        canvas.setFillColor(colors.black)
        canvas.rect(0.5*inch, start_posn-1.2*inch,
                    PAGE_WIDTH-inch, 1.1*inch)
        canvas.line(2.5*inch, start_posn-1.2*inch,
                    2.5*inch, start_posn-0.1*inch)
        canvas.drawString(0.7*inch, start_posn-0.3*inch, 'Company Name:')
        canvas.drawString(2.7*inch, start_posn-0.3*inch,
                          self.details['name'].strip())
        canvas.line(0.5*inch, start_posn-0.4*inch,
                    PAGE_WIDTH-0.5*inch, start_posn-0.4*inch)
        canvas.drawString(0.7*inch, start_posn-0.6*inch, 'Mailing Address:')
        address = ''
        if self.details['address1'].strip() != '':
            address += self.details['address1'].strip() + '<br/>'
        if self.details['address2'].strip() != '':
            address += self.details['address2'].strip() + '<br/>'
        if self.details['city'].strip() != '' or \
                self.details['state_prov'].strip() != '':
            if self.details['city'].strip() != '':
                address += self.details['city'].strip() + ', '
            address += self.details['state_prov'].strip() + '<br/>'
        if self.details['postal_code'].strip() != '':
            address += self.details['postal_code'].strip() + '  '
        address += self.details['country'].strip()
        style_sheet = getSampleStyleSheet()
        style = style_sheet['BodyText']
        para = Paragraph(address, style)
        h = para.wrap(4.7 * inch, 0.9* inch)[1]
        para.drawOn(canvas, 2.7 * inch, start_posn-h-0.35*inch)
        self.start_posn = start_posn-1.45*inch

    def _add_registration_details(self, canvas):
        start_posn = self.start_posn
        reg_detail_dict = {t[0]:t[1] for t in REG_STATUS_OPTIONS}
        canvas.setFillColor(colors.blue)
        canvas.setFont('Helvetica', 10)
        canvas.drawString(0.5*inch, start_posn,
                          'Section D: Registration Details')
        canvas.setLineWidth(1)
        canvas.setFillColor(colors.black)
        canvas.rect(0.5*inch, start_posn-1.3*inch,
                    PAGE_WIDTH-inch, 1.2*inch)
        canvas.line(2.5*inch, start_posn-1.3*inch,
                    2.5*inch, start_posn-0.1*inch)
        canvas.drawString(0.7*inch, start_posn-0.3*inch,
                          'Registration Status:')
        canvas.drawString(2.7*inch, start_posn-0.3*inch,
                          reg_detail_dict[self.details['registration_status']])
        canvas.line(0.5*inch, start_posn-0.4*inch,
                    PAGE_WIDTH-0.5*inch, start_posn-0.4*inch)
        canvas.drawString(0.7*inch, start_posn-0.6*inch, 'Pre-Tax Price:')
        try:
            price = float(self.details['pre_tax_price'])
            gst, hst, qst, inv_total = self._calculate_tax_total(price)
            price = '${:0,.2f}'.format(price)
        except ValueError:
            if self.details['pre_tax_price'] == '':
                price = gst = hst = qst = inv_total = '$0.00'
            else:
                price = 'ERROR: Price Entered Incorrectly'
                gst = hst = qst = inv_total = '?????'
        canvas.drawString(2.7*inch, start_posn-0.6*inch, price)
        canvas.line(0.5*inch, start_posn-0.7*inch,
                    PAGE_WIDTH-0.5*inch, start_posn-0.7*inch)
        canvas.drawString(0.7*inch, start_posn-0.9*inch, 'Taxes:')
        tax_info = ''
        if self.event.gst_charged:
            tax_info += 'GST: ' + gst + ' / '
        if self.event.hst_charged:
            tax_info += 'HST: ' + hst + ' / '
        if self.event.qst_charged:
            tax_info += 'QST: ' + qst + ' / '
        if len(tax_info) > 0:
            tax_info = tax_info[:-3]
        else:
            tax_info = 'No tax charged'
        canvas.drawString(2.7*inch, start_posn-0.9*inch, tax_info)
        canvas.line(0.5*inch, start_posn-1.0*inch,
                    PAGE_WIDTH-0.5*inch, start_posn-1.0*inch)
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(0.7*inch, start_posn-1.2*inch, 'Total Invoice:')
        canvas.drawString(2.7*inch, start_posn-1.2*inch, inv_total)
        self.start_posn = start_posn - 1.55 * inch

    def _add_assistant_details(self, canvas):
        start_posn = self.start_posn
        canvas.setFillColor(colors.blue)
        canvas.setFont('Helvetica', 10)
        canvas.drawString(0.5*inch, start_posn, 'Assistant Details')
        canvas.setFillColor(colors.black)
        canvas.rect(0.5*inch, start_posn-0.9*inch,
                    PAGE_WIDTH-inch, 0.8*inch)
        canvas.line(2.5*inch, start_posn-0.9*inch,
                    2.5*inch, start_posn-0.1*inch)
        canvas.drawString(0.7*inch, start_posn-0.3*inch, 'Assistant:')
        assistant_deets = ''
        new_line = False
        if self.details['assistant_salutation'].strip() != '':
            new_line = True
            assistant_deets += self.details['assistant_salutation'].strip() + ' '
        if self.details['assistant_first_name'].strip() != '':
            new_line = True
            assistant_deets += self.details['assistant_first_name'].strip() + ' '
        if self.details['assistant_last_name'].strip() != '':
            new_line = True
            assistant_deets += self.details['assistant_last_name'].strip() + ' '
        if new_line:
            assistant_deets += '<br/>'
        if self.details['assistant_title'].strip() != '':
            assistant_deets += self.details['assistant_title'].strip()
            assistant_deets += '<br/>'
        if self.details['assistant_email'].strip() != '':
            assistant_deets += 'Email: '
            assistant_deets += self.details['assistant_email'] + '<br/>'
        if self.details['assistant_phone'].strip() != '':
            assistant_deets += 'Phone: ' + self.details['assistant_phone']
        style_sheet = getSampleStyleSheet()
        style = style_sheet['BodyText']
        para = Paragraph(assistant_deets, style)
        h = para.wrap(4.7*inch, 0.8*inch)[1]
        para.drawOn(canvas, 2.7*inch, start_posn-h-0.15*inch)
        self.start_posn = start_posn-1.1*inch

    def _add_notes(self, canvas):
        """
        This is designed to be the last element on the page.
        Don't move it or stuff will break
        """
        start_posn = self.start_posn
        start_posn = self.start_posn
        canvas.setFillColor(colors.blue)
        canvas.setFont('Helvetica', 10)
        canvas.drawString(0.5*inch, start_posn,
                          'Section E - Registration Notes')
        canvas.setFillColor(colors.black)
        canvas.rect(0.5*inch, 0.75*inch,
                    PAGE_WIDTH-inch, start_posn-0.85*inch)
        style_sheet = getSampleStyleSheet()
        style = style_sheet['BodyText']
        para = Paragraph(self.details['registration_notes'], style)
        h=para.wrap(7.1 * inch, start_posn-0.65*inch)[1]
        para.drawOn(canvas, 0.7 * inch, start_posn-h-0.2*inch)

    def _draw_stuff(self, canvas):
        self._add_page_outline(canvas)
        self._add_conference_details(canvas)
        if len(self.details['event_options']) > 0:
            self._add_event_options(canvas)
        self._add_delegate_information(canvas)
        self._add_company_information(canvas)
        self._add_registration_details(canvas)
        if (self.details['assistant_first_name'] or
            self.details['assistant_last_name'] or
            self.details['assistant_email'] or
            self.details['assistant_phone']):
            self._add_assistant_details(canvas)
        # _add_notes must be the last thing drawn
        self._add_notes(canvas)

    def generate_report(self):
        report_name = 'Conference Registration Form'
        buffr = BytesIO()
        styles = getSampleStyleSheet()
        report = canvas.Canvas(buffr, pagesize=letter)
        self._draw_stuff(report)
        report.showPage()
        report.save()
        pdf = buffr.getvalue()
        buffr.close()
        return pdf
