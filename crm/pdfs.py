from io import BytesIO
import os

from infonex_crm.settings import BASE_DIR

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, mm, cm
from reportlab.pdfgen import canvas
# from reportlab.platypus import Paragraph, SimpleDocTemplate

LOGO_PATH = os.path.join(BASE_DIR,
                         'delegate/static/delegate/INFONEX-logo-tag.jpg')
PAGE_HEIGHT = letter[1]
PAGE_WIDTH = letter[0]

class RegForm:
    """
    Generate pdf reg form for a specific crm contact
    """

    def __init__(self, crm_obj, conf_obj, addl_details={}):
        self._pagesize = letter
        self._width, self._height = self._pagesize
        self._person = crm_obj
        self._event = conf_obj
        self._details = addl_details

    def _draw_stuff(self, report):
        # list of subroutines to add stuff to page
        pass

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
