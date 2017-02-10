from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

black = colors.black


def header(canv):
    """
    Adds company logo, keylines and 'INVOICE' to top of page
    :param canv: invoice pdf canvas
    :type canv: reportlab canvas.Canvas object
    """
    canv.setFont('Helvetica-BoldOblique', 16)
    canv.drawString(7.2 * inch, 10.275 * inch,'INVOICE')
    canv.setLineWidth(2)
    canv.line(0.45 * inch, 10.15 * inch, 8.2 * inch, 10.15 * inch)
    canv.setLineWidth(1)
    canv.line(0.45 * inch, 10.15 * inch - 3, 8.2 * inch, 10.15 * inch - 3)
    canv.drawImage('INFONEX-logo-tag.jpg', 0.45 * inch, 10.275 * inch,
                   height=0.5*inch, width=1.875*inch)


def invoice_number_date(canv):
    canv.setFont('Helvetica-Bold', 10)
    canv.drawRightString(7 * inch, 9.8 * inch, 'Invoice Number')
    canv.drawRightString(7 * inch, 9.5 * inch, 'Date')
    canv.setFont('Helvetica', 12)
    canv.drawString(7.2 * inch, 9.8 * inch, '32525')
    canv.drawString(7.2 * inch, 9.5 * inch, '30 Nov 2016')


def customer_info(canv):
    sample_customer = [
        'Ms. Laura Gladwish',
        'Communications Producer',
        'IBM Canada Ltd.',
        '147 Liberty Street',
        'Toronto, ON M6K 3G3',
        'Canada'
    ]
    canv.setFont('Helvetica', 11)
    canv.drawString(0.45 * inch, 9.5 * inch, 'SOLD TO:')
    canv.setFont('Helvetica', 10)
    y = 9.2 * inch
    for line in sample_customer:
        canv.drawString(0.45 * inch, y, line)
        y -= 12


def details_box(canv):
    # draw boxes
    canv.setLineWidth(1)
    canv.rect(0.45 * inch, 5.15 * inch, 7.75 * inch, 2.75 * inch)
    canv.line(0.45 * inch, 7.65 * inch, 8.2 * inch, 7.65 * inch)
    canv.line(1.2 * inch, 5.15 * inch, 1.2 * inch, 7.9 * inch)
    canv.line(7.2 * inch, 5.15 * inch, 7.2 * inch, 7.9 * inch)
    # put in header info
    canv.setFont('Helvetica', 10)
    canv.drawCentredString(0.825 * inch, 7.7 * inch, 'Event No.')
    canv.drawString(1.4 * inch, 7.7 * inch, 'Registration Details')
    canv.drawCentredString(7.7 * inch, 7.7 * inch, 'Amount Due')
    # add order details
    canv.setFont('Helvetica-Bold', 12)
    canv.drawString(1.4 * inch , 7.4 * inch, 'Predictive HR Analytics')
    canv.setFont('Helvetica', 12)
    canv.drawCentredString(0.825 * inch, 7.4 * inch, '1241')
    canv.drawRightString(8.1 * inch, 7.4 * inch, '$9,795.00')
    canv.drawString(1.4 * inch, 7.15 * inch, 'Attendee: Laura Gladwish')
    canv.drawString(1.4 * inch, 6.9 * inch, 'Toronto, ON')
    canv.drawString(1.6 * inch, 6.65 * inch, 'Conference - 28 Mar to 29 Mar 2017')


def totals_box(canv):
    # draw boxes
    canv.setLineWidth(1)
    canv.setFillGray(0.8)
    canv.rect(5.45 * inch, 3.4 * inch, 2.75 * inch, 1.5 * inch, fill=0)
    canv.rect(5.45 * inch, 4.6 * inch , 2.75 * inch, 0.3 * inch, fill=1)
    canv.rect(5.45 * inch, 3.7 * inch, 2.75 * inch, 0.3 * inch, fill=1)
    canv.line(5.45 * inch, 4.3 * inch, 8.2 * inch, 4.3 * inch)
    canv.line(7.2 * inch, 3.4 * inch, 7.2 * inch, 4.9 * inch)
    canv.setFillColor(black)
    # Add text
    canv.setFont('Helvetica', 12)
    canv.drawRightString(7.1 * inch, 4.7 * inch, 'Subtotal:')
    canv.drawRightString(7.1 * inch, 4.4 * inch, 'HST:')
    canv.drawRightString(7.1 * inch, 4.1 * inch, 'GST:')
    canv.setFont('Helvetica-Bold', 12)
    canv.drawRightString(7.1 * inch, 3.8 * inch, 'Total Due:')
    canv.setFont('Helvetica', 12)
    canv.drawRightString(7.1 * inch, 3.5 * inch, 'Invoice Currency:')

    canv.drawRightString(8.1 * inch, 4.7 * inch, '$9,795.00')
    canv.drawRightString(8.1 * inch, 4.4 * inch, '$1,273.35')
    canv.drawRightString(8.1 * inch, 4.1 * inch, '')
    canv.setFont('Helvetica-Bold', 12)
    canv.drawRightString(8.1 * inch, 3.8 * inch, '$11,068.35')
    canv.setFont('Helvetica', 12)
    canv.drawRightString(8.1 * inch, 3.5 * inch, 'CAD')

def memo_box(canv):
    style_sheet = getSampleStyleSheet()
    style = style_sheet['BodyText']
    memo_text = 'Deposit of $2767.09 due December 31, 2016.  Remaining ' \
                'balance of $8301.26 due January 31, 2017.'
    para = Paragraph(memo_text, style)
    para.wrap(3 * inch, 2 * inch)
    para.drawOn(canv, 1.2 * inch, 3.4 * inch)


def footer(canv):
    company_address = [
        'INFONEX',
        '360 Bay Street, Suite 900',
        'Toronto, ON M5H 2V6',
        'Phone: (416) 971-4177',
        'Email: register@infonex.ca',
        'Web: http://www.infonex.ca/1241/index.shtml',
    ]
    canv.setFont('Helvetica-Bold', 10)
    canv.drawString(0.45 * inch, 0.75 * inch,
                    'Please Make Cheques Payable to Infonex Inc.')
    canv.setFont('Helvetica-Bold', 8)
    canv.drawString(0.45 * inch, 0.5 * inch,
                    'GST/HST No: R134050012')
    y = 0.75 *inch
    for line in company_address:
        canv.drawRightString(8.2 * inch, y, line)
        y -= 9.6


def paid_stamp(canv):
    canv.drawImage('PAID.jpg', 6.2 * inch, 5.4 * inch,
                   height=1.0*inch, width=1.6667*inch)


def revised_stamp(canv):
    canv.drawImage('REVISED.jpg', 6.2 * inch, 8.0 * inch,
                   height=1.0*inch, width=2.375*inch)


def create_invoice():
    invoice = canvas.Canvas('invoice.pdf', pagesize=letter)
    header(invoice)
    footer(invoice)
    invoice_number_date(invoice)
    customer_info(invoice)
    details_box(invoice)
    totals_box(invoice)
    memo_box(invoice)
    paid_stamp(invoice)
    revised_stamp(invoice)
    invoice.showPage()  # Closes page
    invoice.save()  # Writes file to disk
