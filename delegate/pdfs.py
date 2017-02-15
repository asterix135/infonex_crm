import os

from .constants import *
from infonex_crm.settings import BASE_DIR

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generate_invoice(canv, reg_details, invoice):
    """
    Generates invoice on supplied canvas; modified in place so nothing returned
    :param canv: ReportLab Canvas
    :param reg_details: RegDetails objects
    :param invoice: Invoice object
    """
    logo_path = os.path.join(BASE_DIR,
                             'delegate/static/delegate/INFONEX-logo-tag.jpg')
    paid_stamp_path = os.path.join(BASE_DIR,
                                   'delegate/static/delegate/PAID.jpg')
    revised_stamp_path = os.path.join(BASE_DIR,
                                      'delegate/static/delegate/REVISED.jpg')
    black = colors.black

    # Header
    canv.setFont('Helvetica-BoldOblique', 16)
    canv.drawString(7.2 * inch, 10.275 * inch,'INVOICE')
    canv.setLineWidth(2)
    canv.line(0.45 * inch, 10.15 * inch, 8.2 * inch, 10.15 * inch)
    canv.setLineWidth(1)
    canv.line(0.45 * inch, 10.15 * inch - 3, 8.2 * inch, 10.15 * inch - 3)
    canv.drawImage(logo_path, 0.45 * inch, 10.275 * inch,
                          height=0.5*inch, width=1.875*inch)

    # Footer
    company_address = [
        'INFONEX',
        '360 Bay Street, Suite 900',
        'Toronto, ON M5H 2V6',
        'Phone: (416) 971-4177',
        'Email: register@infonex.ca',
    ]
    if reg_details.conference.event_web_site:
        company_address.append('Web: ' + reg_details.conference.event_web_site)
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

    # Invoice number & date
    canv.setFont('Helvetica-Bold', 10)
    canv.drawRightString(7 * inch, 9.8 * inch, 'Invoice Number')
    canv.drawRightString(7 * inch, 9.5 * inch, 'Date')
    canv.setFont('Helvetica', 12)
    canv.drawString(7.2 * inch, 9.8 * inch, str(invoice.pk))
    canv.drawString(7.2 * inch, 9.5 * inch,
                           str(reg_details.register_date))

    # Customer Info
    customer_details = []
    if reg_details.registrant.salutation:
        cust_name = reg_details.registrant.salutation + ' '
    else: cust_name = ''
    if reg_details.registrant.first_name:
        cust_name += reg_details.registrant.first_name + ' '
    if reg_details.registrant.last_name:
        cust_name += reg_details.registrant.last_name
    customer_details.append(cust_name)
    if reg_details.registrant.title:
        customer_details.append(reg_details.registrant.title)
    if reg_details.registrant.company.name:
        customer_details.append(reg_details.registrant.company.name)
    if reg_details.registrant.company.address1:
        customer_details.append(reg_details.registrant.company.address1)
    if reg_details.registrant.company.address2:
        customer_details.append(reg_details.registrant.company.address2)
    if reg_details.registrant.company.city:
        city_line = reg_details.registrant.company.city
    else:
        city_line = ''
    if reg_details.registrant.company.state_prov:
        if len(city_line) > 0:
            city_line += ', '
        city_line += reg_details.registrant.company.state_prov + ' '
    if reg_details.registrant.company.postal_code:
        city_line += reg_details.registrant.company.postal_code
    if len(city_line) > 0:
        customer_details.append(city_line)
    if reg_details.registrant.company.country:
        customer_details.append(reg_details.registrant.company.country)
    canv.setFont('Helvetica', 11)
    canv.drawString(0.45 * inch, 9.5 * inch, 'SOLD TO:')
    canv.setFont('Helvetica', 10)
    y = 9.2 * inch
    for line in customer_details:
        canv.drawString(0.45 * inch, y, line)
        y -= 12

    # Details Box
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
    canv.drawString(1.4 * inch , 7.4 * inch, reg_details.conference.title)
    canv.setFont('Helvetica', 12)
    canv.drawCentredString(0.825 * inch, 7.4 * inch,
                                  reg_details.conference.number)
    canv.drawRightString(8.1 * inch, 7.4 * inch,
                                '${:,.2f}'.format(invoice.pre_tax_price))
    canv.drawString(1.4 * inch, 7.15 * inch, 'Attendee: ' + cust_name)
    canv.drawString(1.4 * inch, 6.9 * inch,
                           reg_details.conference.city + ', ' + \
                               reg_details.conference.state_prov)
    reg_option_list = []
    if reg_details.regeventoptions_set.all().count() > 0:
        for detail in reg_details.regeventoptions_set.all():
            start_date = detail.option.startdate.strftime('%-d %B, %Y')
            end_date = detail.option.enddate.strftime('%-d %B, %Y')
            conf_detail = detail.option.name + ' - ' + start_date
            if start_date != end_date:
                conf_detail += ' to ' + end_date
            reg_option_list.append(conf_detail)
    else:
        detail_date = reg_details.conference.date_begins.strftime('%-d %B, %Y')
        conf_detail = 'Conference - ' + detail_date
        reg_option_list.append(conf_detail)
    y = 6.65 * inch
    for option in reg_option_list:
        canv.drawString(1.6 * inch, y, option)
        y -= 14

    # Totals box
    canv.setLineWidth(1)
    canv.setFillGray(0.8)
    canv.rect(5.45 * inch, 3.4 * inch, 2.75 * inch, 1.5 * inch, fill=0)
    canv.rect(5.45 * inch, 4.6 * inch , 2.75 * inch, 0.3 * inch, fill=1)
    canv.rect(5.45 * inch, 3.7 * inch, 2.75 * inch, 0.3 * inch, fill=1)
    canv.line(5.45 * inch, 4.3 * inch, 8.2 * inch, 4.3 * inch)
    canv.line(7.2 * inch, 3.4 * inch, 7.2 * inch, 4.9 * inch)
    canv.setFillColor(black)
    # Add text
    tax_list = []
    tax_amounts = []
    if reg_details.conference.gst_charged:
        tax_list.append('GST')
        tax_amounts.append(invoice.pre_tax_price * invoice.gst_rate)
    if reg_details.conference.hst_charged:
        tax_list.append('HST')
        tax_amounts.append(invoice.pre_tax_price * invoice.hst_rate)
    if reg_details.conference.qst_charged:
        tax_list.append('QST')
        tax_amounts.append(invoice.pre_tax_price * (1 + invoice.gst_rate) *
                           invoice.qst_rate)
    canv.setFont('Helvetica', 12)
    canv.drawRightString(7.1 * inch, 4.7 * inch, 'Subtotal:')
    if len(tax_list) > 0:
        canv.drawRightString(7.1 * inch, 4.4 * inch, tax_list[0])
    if len(tax_list) > 1:
        canv.drawRightString(7.1 * inch, 4.1 * inch, tax_list[1])
    canv.setFont('Helvetica-Bold', 12)
    canv.drawRightString(7.1 * inch, 3.8 * inch, 'Total Due:')
    canv.setFont('Helvetica', 12)
    canv.drawRightString(7.1 * inch, 3.5 * inch, 'Invoice Currency:')
    # Add specific totals
    canv.drawRightString(8.1 * inch, 4.7 * inch,
                         '${:,.2f}'.format(invoice.pre_tax_price))  # Subtotal
    if len(tax_amounts) > 0:
        canv.drawRightString(8.1 * inch, 4.4 * inch,
                             '${:,.2f}'.format(tax_amounts[0]))  # tax1
    if len(tax_amounts) > 1:
        canv.drawRightString(8.1 * inch, 4.1 * inch,
                             '${:,.2f}'.format(tax_amounts[1]))  # tax2
    canv.setFont('Helvetica-Bold', 12)
    canv.drawRightString(8.1 * inch, 3.8 * inch,
                         '${:,.2f}'.format(invoice.pre_tax_price +
                                           sum(tax_amounts)))  # Total Due
    canv.setFont('Helvetica', 12)
    canv.drawRightString(8.1 * inch, 3.5 * inch,
                         reg_details.conference.billing_currency)  # Currency

    # Notes box
    style_sheet = getSampleStyleSheet()
    style = style_sheet['BodyText']
    para = Paragraph(invoice.invoice_notes, style)
    para.wrap(3 * inch, 2 * inch)
    para.drawOn(canv, 1.2 * inch, 3.4 * inch)

    # Add stamps
    if reg_details.registration_status in PAID_STATUS_VALUES:
        canv.drawImage(paid_stamp_path, 6.2 * inch, 5.4 * inch,
                       height=1.0*inch, width=1.6667*inch)

    if invoice.revised_flag:
        canv.drawImage(revised_stamp_path, 6.2 * inch, 8.0 * inch,
                       height=1.0*inch, width=2.375*inch)


def generate_reg_note(canv, reg_details, invoice=None):
    """
    Generates registration note on supplied canvas;
    modified in place so nothing returned
    :param canv: ReportLab Canvas
    :param reg_details: RegDetails objects
    :param invoice: Invoice object
    """
    logo_path = os.path.join(BASE_DIR,
                             'delegate/static/delegate/INFONEX-logo-tag.jpg')
    black = colors.black
