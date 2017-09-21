from datetime import datetime
from io import BytesIO
import os

from registration.models import EventOptions
from infonex_crm.settings import BASE_DIR

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, mm, cm
from reportlab.pdfgen import canvas

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

    def __init__(self, crm_obj, conf_obj, user, addl_details):
        self.person = crm_obj
        self.event = conf_obj
        self.user = user
        self.details = addl_details

    def _1_add_page_outline(self, canvas):
        canvas.setLineWidth(2)
        canvas.rect(cm, cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-2*cm)
        canvas.drawImage(LOGO_PATH, 0.5*inch, 10 * inch,
                       height=0.5*inch, width=1.875*inch)
        canvas.setFont('Helvetica-Bold', 24)
        canvas.drawRightString(PAGE_WIDTH-(0.5*inch), 10.15*inch,
                               'REGISTRATION FORM')
        footer_text = 'This form created on '
        footer_text += datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
        footer_text += ' by '
        footer_text += self.user.first_name + ' ' + self.user.last_name
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(PAGE_WIDTH-(0.5*inch), 0.5*inch, footer_text)

    def _2_add_conference_details(self, canvas):
        canvas.setFillColor(colors.blue)
        canvas.setFont('Helvetica', 10)
        canvas.drawString(0.5*inch, 9.5*inch,
                          'Section A - Conference Information')
        canvas.setFillColor(colors.black)
        canvas.setLineWidth(1)
        canvas.rect(0.5*inch, 9*inch,
                    PAGE_WIDTH-inch, 0.4*inch)
        canvas.line(2.5*inch, 9*inch, 2.5*inch, 9.4*inch)
        canvas.setFillColor(colors.red)
        canvas.drawString(0.7*inch, 9.15*inch,
                          self.event.number)
        canvas.setFillColor(colors.black)
        canvas.drawString(2.7*inch, 9.15*inch,
                          self.event.title)

    def _3_add_event_options(self, canvas):
        num_options = len(self.details['event_options'])
        canvas.setFont('Helvetica', 10)
        canvas.setLineWidth(1)
        canvas.setFillColor(colors.blue)
        canvas.drawString(0.5*inch, 8.75*inch,
                          'Conference Options Selected')
        canvas.setFillColor(colors.black)
        canvas.rect(0.5*inch, (8.65-num_options*0.4)*inch,
                    PAGE_WIDTH-inch, num_options*0.4*inch)
        option_height = 8.4
        for option in self.details['event_options']:
            event_option = EventOptions.objects.get(pk=option)
            option_text = event_option.name + ':  '
            option_text += event_option.startdate.strftime('%-d %B, %Y')
            if event_option.enddate != event_option.startdate:
                option_text += ' to '
                option_text += event_option.enddate.strftime('%-d %B, %Y')
            canvas.drawString(0.7 * inch, option_height * inch, option_text)
            canvas.line(0.5*inch, (option_height-0.15) * inch,
                        PAGE_WIDTH-0.5*inch, (option_height-0.15) * inch)
            option_height -= 0.4
        return 8.75 - option_height - 0.2

    def _4_add_delegate_information(self, canvas, offset=0):
        canvas.setFillColor(colors.blue)
        canvas.setFont('Helvetica', 10)
        canvas.drawString(0.5*inch, (8.5-offset)*inch,
                          'Section B - Delegate Information')
        canvas.setLineWidth(1)
        canvas.setFillColor(colors.black)
        canvas.rect(0.5*inch, (5.9-offset)*inch,
                    PAGE_WIDTH-inch, 2.5*inch)
        canvas.drawString(0.7 * inch, (8.15-offset)*inch, 'Delegate Name:')
        name = ''
        if self.details['salutation'] not in ('', None):
            name += self.details['salutation'] + ' '
        if self.details['first_name'] not in ('', None):
            name += self.details['first_name'] + ' '
        name += self.details['last_name']
        canvas.drawString(2.7 * inch, (8.15-offset)*inch, name)
        canvas.line(0.5*inch, (8-offset)*inch,
                    PAGE_WIDTH-0.5*inch, (8-offset)*inch)
        canvas.drawString(0.7*inch, (7.75-offset)*inch, 'Delegate Title:')
        # # Put name in here
        # canvas.line(0.5*inch, 7.6*inch, PAGE_WIDTH-0.5*inch, 7.6*inch)
        # canvas.drawString(0.7*inch, 7.35*inch, 'Title:')
        # # Put title in here
        # canvas.line(0.5*inch, 7.2*inch, PAGE_WIDTH-0.5*inch, 7.2*inch)

    def _draw_stuff(self, canvas):
        self._1_add_page_outline(canvas)
        self._2_add_conference_details(canvas)
        if len(self.details['event_options']) > 0:
            offset = self._3_add_event_options(canvas)
        else:
            offset = 0
        self._4_add_delegate_information(canvas, offset)

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
