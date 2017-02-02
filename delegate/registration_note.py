from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


black = colors.black


def header(canv):
    """
    Adds company logo, keylines and 'REGISTRATION NOTE' to top of page
    :param canv: pdf canvas
    :type canv: reportlab canvas.Canvas object
    """
    canv.setFont('Helvetica-BoldOblique', 16)
    canv.drawRightString(8.2 * inch, 10.275 * inch, 'REGISTRATION NOTE')
    canv.setLineWidth(2)
    canv.line(0.45 * inch, 10.15 * inch, 8.2 * inch, 10.15 * inch)
    canv.setLineWidth(1)
    canv.line(0.45 * inch, 10.15 * inch - 3, 8.2 * inch, 10.15 * inch - 3)
    canv.drawImage('INFONEX-logo-tag.jpg', 0.45 * inch, 10.275 * inch,
                   height=0.5*inch, width=1.875*inch)


def status_box(canv):
    style_sheet = getSampleStyleSheet()
    style = style_sheet['BodyText']
    canv.rect(6 * inch, 9.2 * inch, 2.2 * inch, 0.75 * inch)
    canv.setFont('Helvetica-Bold', 11)
    canv.drawRightString(6.7 * inch, 9.52 * inch, 'Status:')
    status_text = 'Sponsorship - Part Paid'
    para = Paragraph(status_text, style)
    h = para.wrap(1.25 * inch, 1 * inch)[1]
    para.drawOn(canv, 6.8 * inch,  9.52 * inch - 2 - 0.5 * (h-12))


def conference_details(canv):
    style = ParagraphStyle(
        'default',
        fontName = 'Helvetica',
        fontSize = 11,
        leading = 13,
    )
    canv.setFont('Helvetica-Bold', 11)
    canv.drawRightString(1.6 * inch, 9.52 * inch, 'Conference:')

    conf_name = '<u>' + '1154 - Operational Risk Canada 2015' + '</u>'
    para = Paragraph(conf_name, style)
    para.wrap(3 * inch, 0.5 * inch)
    para.drawOn(canv, 1.7 * inch, 9.52 * inch - 2)
    canv.setFont('Helvetica-Bold', 9)
    canv.drawRightString(1.6 * inch, 9.52 * inch - 13, 'Dates:')
    canv.drawRightString(1.6 * inch, 9.52 * inch - 24, 'Venue:')
    canv.setFont('Helvetica', 9)
    canv.drawString(1.7 * inch, 9.52 * inch - 13, '20 Oct 2015 - 21 Oct 2015')
    canv.drawString(1.7 * inch, 9.52 * inch - 24,
                    'Toronto at the Novotel Toronto Centre')


def purchase_details(canv):
    canv.setFont('Helvetica-Bold', 11)
    canv.drawRightString(1.6 * inch, 8.7 * inch, 'Purchase Date:')
    canv.drawRightString(6.0 * inch, 8.7 * inch, 'Invoice Number:')
    canv.setFont('Helvetica', 11)
    canv.drawString(1.7 * inch, 8.7 * inch, '22 May 2015')
    canv.drawString(6.1 * inch, 8.7 * inch, '31111')
    canv.setFont('Helvetica-Bold', 9)
    canv.drawRightString(1.6 * inch, 8.7 * inch - 13, 'Priority Code:')
    canv.drawRightString(6.0 * inch, 8.7 * inch - 13, 'Payment Method:')
    canv.drawRightString(1.6 * inch, 8.7 * inch - 25, 'Sales Credit:')
    canv.drawRightString(6.0 * inch, 8.7 * inch - 25, 'Payment Date:')
    canv.drawRightString(1.6 * inch, 8.7 * inch - 37, 'PD Credit:')
    canv.drawRightString(6.0 * inch, 8.7 * inch - 37, 'Cancellation Date:')
    canv.setFont('Helvetica', 9)
    canv.drawString(1.7 * inch, 8.7 * inch - 13, 'Unknown')
    canv.drawString(6.1 * inch, 8.7 * inch - 13, 'MasterCard')
    canv.drawString(1.7 * inch, 8.7 * inch - 25, 'Marketing')
    canv.drawString(6.1 * inch, 8.7 * inch - 25, '29 May 2015')
    canv.drawString(1.7 * inch, 8.7 * inch - 37, 'Linette DeGraaf')
    canv.drawString(6.1 * inch, 8.7 * inch - 37, '30 May 2015')


def buyer_details(canv):
    canv.setFont('Helvetica-Bold', 11)
    canv.drawRightString(1.6 * inch, 7.7 * inch, 'Sold To:')
    canv.setFont('Helvetica', 11)
    canv.drawString(1.7 * inch, 7.7 * inch, 'Farm Credit Canada')
    canv.drawString(1.7 * inch, 7.7 * inch - 13, '1800 Hamilton Street')
    canv.drawString(1.7 * inch, 7.7 * inch - 26, 'P.O. Box 4320')
    canv.drawString(1.7 * inch, 7.7 * inch - 39, 'Regina, SK')
    canv.drawString(1.7 * inch, 7.7 * inch - 52, 'S4P 4L3')
    canv.drawString(1.7 * inch, 7.7 * inch - 65, 'Canada')
    canv.setFont('Helvetica-Bold', 9)
    canv.drawRightString(6.0 * inch, 7.7 * inch, 'Phone:')
    canv.drawRightString(6.0 * inch, 7.7 * inch - 11, 'Email:')
    canv.drawRightString(1.6 * inch, 6.5 * inch, 'Company ID No:')
    canv.drawRightString(1.6 * inch, 6.2 * inch, 'GST/HST Exemption No:')
    canv.drawRightString(1.6 * inch, 6.2 * inch - 11, 'QST Exemption No:')
    canv.drawRightString(6.0 * inch, 7.0 * inch, 'Secondary Contact')
    canv.setFont('Helvetica', 9)
    canv.drawString(6.1 * inch, 7.7 * inch, '(306) 780-6484')
    canv.drawString(1.7 * inch, 6.5 * inch, '44270')
    canv.drawString(1.7 * inch, 6.2 * inch, '1234567790')
    canv.drawString(1.7 * inch, 6.2 * inch - 11, '0987654321')
    canv.drawString(6.1 * inch, 7.0 * inch, 'Mary Smith')
    canv.drawString(6.1 * inch, 7.0 * inch - 11, '416-555-1212')
    canv.drawString(6.1 * inch, 7.0 * inch - 22, 'mary_smith@gmail.com')
    style = ParagraphStyle(
        'default',
        fontName = 'Helvetica',
        fontSize = 9,
        leading = 11,
    )
    email_address = 'vankatesh.bhat@fcc.ca'
    para = Paragraph(email_address, style)
    h = para.wrap(2.1 * inch, 1 * inch)[1]
    para.drawOn(canv, 6.1 * inch, 7.7 * inch - h - 2)


def registrant_details(canv):
    canv.line(0.45 * inch, 5.8 * inch, 8.2 * inch, 5.8 * inch)
    style = ParagraphStyle(
        'default',
        fontName = 'Helvetica-Bold',
        fontSize = 11,
        leading = 13,
    )
    para = Paragraph('<u>Registrant Details</u>', style)
    para.wrap(3 * inch, 0.5 * inch)
    para.drawOn(canv, 0.45 * inch, 5.6 * inch - 2)
    canv.setFont('Helvetica-Bold', 9)
    canv.drawString(0.45 * inch, 5.4 * inch, 'Name')
    canv.drawString(2.75 * inch, 5.4 * inch, 'Options')
    canv.drawRightString(8.1 * inch, 5.4 * inch, 'Price')
    canv.line(0.45 * inch, 5.4 * inch - 5, 8.2 * inch, 5.4 * inch -5)
    style = ParagraphStyle(
        'default',
        fontName = 'Helvetica',
        fontSize = 9,
        leading = 11,
    )
    name = 'Venkatesh Bhat'
    para = Paragraph(name, style)
    h = para.wrap(2.1 * inch, 1 * inch)[1]
    para.drawOn(canv, 0.45 * inch, 5.1 * inch - h + 9)
    conf_option = 'Conference - 20 Oct to 21 Oct 2015'
    para = Paragraph(conf_option, style)
    h = para.wrap(3.5 * inch, 1.0 * inch)[1]
    para.drawOn(canv, 2.75 * inch, 5.1 * inch - h + 9)
    canv.setFont('Helvetica', 9)
    canv.drawRightString(8.1 * inch, 5.1 * inch, '$1,499.00')


def notes(canv):
    canv.setFont('Helvetica-Bold', 9)
    canv.drawString(0.45 * inch, 4.2 * inch, 'Notes:')
    style = ParagraphStyle(
        'default',
        fontName = 'Helvetica',
        fontSize = 9,
        leading = 11,
    )
    memo_text = 'Deposit of $2767.09 due December 31, 2016.  Remaining ' \
                'balance of $8301.26 due January 31, 2017.'
    para = Paragraph(memo_text, style)
    h = para.wrap(4 * inch, 2 * inch)[1]
    para.drawOn(canv, 0.45 * inch, 4.2 * inch - h)


def cost_details(canv):
    canv.line(6.2 * inch, 4.7 * inch, 8.2 * inch, 4.7 * inch)
    canv.rect(7.2 * inch, 3.3 * inch, 1.0 * inch, 0.5 * inch)
    canv.setFont('Helvetica-Bold', 9)
    canv.drawRightString(7.1 * inch, 4.5 * inch, 'Pre-Tax Total:')
    canv.drawRightString(7.1 * inch, 4.5 * inch - 12, 'GST:')
    canv.drawRightString(7.1 * inch, 4.5 * inch - 24, 'HST:')
    canv.drawRightString(7.1 * inch, 4.5 * inch - 36, 'QST:')
    canv.drawRightString(7.1 * inch, 3.5 * inch, 'Total Invoice:')
    canv.drawRightString(8.1 * inch, 3.5 * inch, '$1,693.87')
    canv.drawRightString(7.1 * inch, 3.1 * inch, 'Currency:')
    canv.drawRightString(7.1 * inch, 3.1 * inch - 12, 'BOC Conversion Rate')
    canv.drawRightString(7.1 * inch, 3.1 * inch - 24, 'C$ Equivalent (pre-tax)')
    canv.drawRightString(7.1 * inch, 3.1 * inch - 36, 'C$ Equivalent (total)')

    canv.setFont('Helvetica', 9)
    canv.drawRightString(8.1 * inch, 4.5 * inch, '$1,499.00')
    canv.drawRightString(8.1 * inch, 4.5 * inch - 12, '$0.00')
    canv.drawRightString(8.1 * inch, 4.5 * inch - 24, '$194.87')
    canv.drawRightString(8.1 * inch, 4.5 * inch - 36, '$0.00')
    canv.drawRightString(8.1 * inch, 3.1 * inch, 'CAD')
    canv.drawRightString(8.1 * inch, 3.1 * inch - 12, '1.4532')
    canv.drawRightString(8.1 * inch, 3.1 * inch - 24, '$1,499.00')
    canv.drawRightString(8.1 * inch, 3.1 * inch - 36, '$1,693.87')


def staff_user_details(canv):
    canv.setFont('Helvetica-Bold', 9)
    canv.drawRightString(1.56 * inch, 0.5 * inch,
                         'Record Created By:')
    canv.drawRightString(1.56 * inch, 0.5 * inch - 12,
                         'Last Modified By:')
    canv.setFont('Helvetica', 9)
    canv.drawString(1.66 * inch, 0.5 * inch,
                    'Alona Glikin - 2016-11-30 4:32:31 PM')
    canv.drawString(1.66 * inch, 0.5 * inch -12,
                    'Alona Glikin - 2016-01-25 10:35:22 AM')


def create_registration_note():
    reg_note = canvas.Canvas('reg_note.pdf', pagesize=letter)
    header(reg_note)
    status_box(reg_note)
    conference_details(reg_note)  # Needs work on conference name
    purchase_details(reg_note)
    buyer_details(reg_note)
    registrant_details(reg_note)
    notes(reg_note)
    cost_details(reg_note)
    staff_user_details(reg_note)

    reg_note.showPage()  # closes page
    reg_note.save()  # saves to disk
