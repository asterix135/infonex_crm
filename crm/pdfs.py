from io import BytesIO
import os

from infonex_crm.settings import BASE_DIR

from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, mm, cm
from reportlab.pdfgen import canvas
# from reportlab.platypus import Paragraph, SimpleDocTemplate

LOGO_PATH = os.path.join(
    BASE_DIR,
    'delegate/static/delegate/INFONEX-logo-tag.jpg'
)
PAGE_HEIGHT = letter[1]
PAGE_WIDTH = letter[0]
BLACK = colors.black

class RegFormPdf:
    """
    Generate pdf reg form for a specific crm contact
    """

    def __init__(self, crm_obj, conf_obj, user, addl_details):
        self.person = crm_obj
        self.event = conf_obj
        self.user = user
        self.details = addl_details

    def _1_page_outline(self, canvas):
        canvas.setLineWidth(2)
        canvas.rect(cm, cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-2*cm)
        canvas.drawImage(LOGO_PATH, 0.5*inch, 10 * inch,
                       height=0.5*inch, width=1.875*inch)
        canvas.setFont('Helvetica-Bold', 24)
        canvas.drawRightString(PAGE_WIDTH-(0.5*inch), 10.15*inch,
                               'REGISTRATION FORM')
        footer_text = 'This form created on '
        footer_text += timezone.now().strftime('%Y-%m-%d %I:%M:%S %p')
        footer_text += ' by '
        footer_text += self.user.first_name + ' ' + self.user.last_name
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(PAGE_WIDTH-(0.5*inch), 0.5*inch, footer_text)


    def _draw_stuff(self, canvas):
        # list of subroutines to add stuff to page
        self._1_page_outline(canvas)

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
