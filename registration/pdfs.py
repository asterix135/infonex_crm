import os
import pytz
from functools import partial

from django.utils import timezone

from .constants import *
from infonex_crm.settings import BASE_DIR

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm, cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

LOGO_PATH = os.path.join(BASE_DIR,
                         'delegate/static/delegate/INFONEX-logo-tag.jpg')
PAGE_HEIGHT = letter[1]
PAGE_WIDTH = letter[0]


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_footer(self, page_count):
        width, height = self._pagesize
        print_date = timezone.now().strftime('%-d %B, %Y')
        # Change the position of this to wherever you want the page number to be
        self.setFont('Helvetica-Bold', 10)
        self.drawString(36, 0.5 * inch,
                        "Page %d of %d" % (self._pageNumber, page_count))
        self.drawRightString(width - 36, 0.5 * inch, print_date)
        copyright_notice = '© ' + timezone.now().strftime('%Y') + ' Infonex Inc.'
        self.drawCentredString(width / 2, 0.5 * inch, copyright_notice)


class ConferenceReportPdf:
    """
    Class to manage generation and delivery of pdfs
    """

    def __init__(self, buffer, event, sort='company'):
        self._buffer = buffer
        self._pagesize = letter
        self._width, self._height = self._pagesize
        self._event = event
        self._sort = sort

    def generate_delegate_list(self):
        report_name = 'Delegate List - CONFIDENTIAL'
        buffer = self._buffer
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(buffer,
                                rightMargin=inch / 2,
                                leftMargin=inch / 2,
                                topMargin=1.6 * inch,
                                bottomMargin=inch * 0.75,
                                pagesize=self._pagesize)
        elements = []
        table_data = []
        header_style = styles['h4']
        header_style.alignment = TA_LEFT
        cell_style = styles['BodyText']
        cell_style.alignment = TA_LEFT
        table_data.append([
            Paragraph('Delegate Name', header_style),
            Paragraph('Title', header_style),
            Paragraph('Company', header_style)
        ])
        if self._sort == 'name':
            sorts = ['registrant__last_name',
                     'registrant__first_name',
                     'registrant__company__name']
        elif self._sort == 'title':
            sorts = ['registrant__title',
                     'registrant__company__name',
                     'registrant__last_name',
                     'registrant__first_name']
        else:
            sorts = ['registrant__company__name',
                     'registrant__title',
                     'registrant__last_name',
                     'registrant__first_name']
        reg_list = self._event.regdetails_set.all().order_by(*sorts)
        for i, reg_detail in enumerate(reg_list):
            name = Paragraph(
                reg_detail.registrant.first_name + ' ' + \
                    reg_detail.registrant.last_name,
                cell_style
            )
            title = Paragraph(
                reg_detail.registrant.title,
                cell_style
            )
            company = Paragraph(
                reg_detail.registrant.company.name,
                cell_style
            )
            table_data.append([name, title, company])
        table = Table(table_data,
                      colWidths=[doc.width/3.0]*3,
                      repeatRows=1)
        table.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1, 0), 2, colors.black),
            ('LINEBELOW', (0,0), (-1, 0), 1, colors.black),
            ('VALIGN', (0,0), (-1, -1), 'TOP'),
        ]))
        elements.append(table)
        doc.build(elements,
                  onFirstPage=partial(self._header, event=self._event,
                                      report_title = report_name),
                  onLaterPages=partial(self._header, event=self._event,
                                       report_title = report_name),
                  canvasmaker=NumberedCanvas)

        pdf = buffer.getvalue()
        return pdf

    def generate_no_name_list(self):
        report_name = 'Delegate List - CONFIDENTIAL'
        buffer = self._buffer
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(buffer,
                                rightMargin=inch / 2,
                                leftMargin=inch / 2,
                                topMargin=1.6 * inch,
                                bottomMargin=inch * 0.75,
                                pagesize=self._pagesize)
        elements = []
        table_data = []
        header_style = styles['h4']
        header_style.alignment = TA_LEFT
        cell_style = styles['BodyText']
        cell_style.alignment = TA_LEFT
        table_data.append([
            Paragraph('Title', header_style),
            Paragraph('Company', header_style)
        ])
        if self._sort == 'title':
            sorts = ['registrant__title',
                     'registrant__company__name']
        else:
            sorts = ['registrant__company__name',
                     'registrant__title']
        reg_list = self._event.regdetails_set.all().order_by(*sorts)
        for i, reg_detail in enumerate(reg_list):
            title = Paragraph(
                reg_detail.registrant.title,
                cell_style
            )
            company = Paragraph(
                reg_detail.registrant.company.name,
                cell_style
            )
            table_data.append([title, company])
        table = Table(table_data,
                      colWidths=[doc.width/2.0]*2,
                      repeatRows=1)
        table.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1, 0), 2, colors.black),
            ('LINEBELOW', (0,0), (-1, 0), 1, colors.black),
            ('VALIGN', (0,0), (-1, -1), 'TOP'),
        ]))
        elements.append(table)
        doc.build(elements,
                  onFirstPage=partial(self._header, event=self._event,
                                      report_title = report_name),
                  onLaterPages=partial(self._header, event=self._event,
                                       report_title = report_name),
                  canvasmaker=NumberedCanvas)

        pdf = buffer.getvalue()
        return pdf

    def generate_registration_list(self):
        report_name = 'Registration List - CONFIDENTIAL'
        buffer = self._buffer
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(buffer,
                                rightMargin=inch / 2,
                                leftMargin=inch / 2,
                                topMargin=1.6 * inch,
                                bottomMargin=inch * 0.75,
                                pagesize=self._pagesize)
        elements = []
        table_data = []
        cell_style = styles['BodyText']
        cell_style.alignment = TA_LEFT
        if self._sort == 'name':
            sorts = ['registrant__last_name',
                     'registrant__first_name',
                     'registrant__company__name']
        elif self._sort == 'title':
            sorts = ['registrant__title',
                     'registrant__company__name',
                     'registrant__last_name',
                     'registrant__first_name']
        else:
            sorts = ['registrant__company__name',
                     'registrant__title',
                     'registrant__last_name',
                     'registrant__first_name']
        reg_list = self._event.regdetails_set.all().order_by(*sorts)
        for i, reg_detail in enumerate(reg_list):
            name = Paragraph(
                reg_detail.registrant.first_name + ' ' + \
                    reg_detail.registrant.last_name,
                cell_style
            )
            title = Paragraph(
                reg_detail.registrant.title,
                cell_style
            )
            company = Paragraph(
                reg_detail.registrant.company.name,
                cell_style
            )
            table_data.append([name, title, company])
        table = Table(table_data,
                      colWidths=[cm * 3.5, cm * 3, cm * 5.5,
                                 cm * 3, cm, cm * 3])
        table.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1, 0), 2, colors.black),
            ('LINEBELOW', (0,0), (-1, 0), 1, colors.black),
            ('VALIGN', (0,0), (-1, -1), 'TOP'),
        ]))
        elements.append(table)
        doc.build(elements,
                  onFirstPage=partial(self._header, event=self._event,
                                      report_title = report_name),
                  onLaterPages=partial(self._header, event=self._event,
                                       report_title = report_name),
                  canvasmaker=NumberedCanvas)

        pdf = buffer.getvalue()
        return pdf

    @staticmethod
    def _header(canvas, doc, event, report_title):
        canvas.saveState()
        styles = getSampleStyleSheet()
        canvas.drawImage(LOGO_PATH, 0.45 * inch, PAGE_HEIGHT - inch * 0.75,
                         height=0.5*inch, width=1.875*inch)
        canvas.setFont('Helvetica-Bold', 18)
        y_coord = PAGE_HEIGHT - inch * 0.45
        canvas.drawString(2.75 * inch, y_coord, report_title)
        canvas.setFont('Helvetica', 16)
        event_title = str(event.number) + ' - ' + event.title
        y_coord -= 18
        canvas.drawString(2.75 * inch, y_coord, event_title)
        event_date = event.date_begins.strftime('%-d %B, %Y')
        y_coord -= 14
        canvas.setFont('Helvetica', 12)
        canvas.drawString(2.75 * inch, y_coord, event_date)
        event_venue = ''
        if event.hotel:
            event_venue += event.hotel.name + ': '
        event_venue += event.city + ', ' + event.state_prov
        y_coord -= 14
        canvas.drawString(2.75 * inch, y_coord, event_venue)
        canvas.setFont('Helvetica', 16)
        y_coord -= 30
        canvas.drawString(2.75 * inch, y_coord, 'Do Not Copy or Distribute')
        canvas.restoreState()
