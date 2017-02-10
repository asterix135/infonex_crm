from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT

from datetime import datetime, timedelta

def build_report(buffer, contact_qs):
    styles = getSampleStyleSheet()

def build_data():
    styles = getSampleStyleSheet()
    cell_style = styles['BodyText']
    cell_style.alignment = TA_LEFT
    data = []
    for i in range(100):
        date = str((datetime.today() - timedelta(days=i)).date())
        date = Paragraph(date, cell_style)
        person = 'George Jetson<br/>Flyboy<br/>Spacely Sprockets'
        person = Paragraph(person, cell_style)
        notes = 'blah blah blah blah blah'
        notes = Paragraph(notes, cell_style)
        data.append([date, person, notes])
    return data


def main():
    styles = getSampleStyleSheet()
    report_details = []
    title = Paragraph('Call Note Report', styles['title'])
    report_details.append(title)
    conf_details = Paragraph('123 - Test Conference 123 (MaryAnne)', styles['h2'])
    report_details.append(conf_details)

    data = build_data()
    call_detail_table = Table(data, [inch, 2 * inch, 4.5 * inch])
    call_detail_table.setStyle(TableStyle([('VALIGN', (0,0), (-1, -1), 'TOP')]))
    report_details.append(call_detail_table)
    report = SimpleDocTemplate('call_report.pdf', pagesize=letter,
                               leftMargin=inch, rightMargin = inch)
    report.build(report_details)


if __name__ == '__main__':
    main()
