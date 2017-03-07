import os
import pytz

from .constants import *
from infonex_crm.settings import BASE_DIR

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


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

    # Header
    canv.setFont('Helvetica-BoldOblique', 16)
    canv.drawRightString(8.2 * inch, 10.275 * inch, 'REGISTRATION NOTE')
    canv.setLineWidth(2)
    canv.line(0.45 * inch, 10.15 * inch, 8.2 * inch, 10.15 * inch)
    canv.setLineWidth(1)
    canv.line(0.45 * inch, 10.15 * inch - 3, 8.2 * inch, 10.15 * inch - 3)
    canv.drawImage(logo_path, 0.45 * inch, 10.275 * inch,
                   height=0.5*inch, width=1.875*inch)

    # Status Box
    style_sheet = getSampleStyleSheet()
    style = style_sheet['BodyText']
    canv.rect(6 * inch, 9.2 * inch, 2.2 * inch, 0.75 * inch)
    canv.setFont('Helvetica-Bold', 11)
    canv.drawRightString(6.7 * inch, 9.52 * inch, 'Status:')
    # status_text = reg_details.get_registration_status_display()
    para = Paragraph(reg_details.get_registration_status_display(), style)
    h = para.wrap(1.25 * inch, 1 * inch)[1]
    para.drawOn(canv, 6.8 * inch,  9.52 * inch - 2 - 0.5 * (h-12))

    # Conference details
    style = ParagraphStyle(
        'default',
        fontName = 'Helvetica',
        fontSize = 11,
        leading = 13,
    )
    canv.setFont('Helvetica-Bold', 11)
    canv.drawRightString(1.6 * inch, 9.52 * inch, 'Conference:')
    conf_name = '<u>' + reg_details.conference.number + ' - ' + \
        reg_details.conference.title + '</u>'
    para = Paragraph(conf_name, style)
    para.wrap(3 * inch, 0.5 * inch)
    para.drawOn(canv, 1.7 * inch, 9.52 * inch - 2)
    canv.setFont('Helvetica-Bold', 9)
    canv.drawRightString(1.6 * inch, 9.52 * inch - 13, 'Start Date:')
    canv.drawRightString(1.6 * inch, 9.52 * inch - 24, 'Venue:')
    canv.setFont('Helvetica', 9)
    canv.drawString(1.7 * inch, 9.52 * inch - 13,
                    reg_details.conference.date_begins.strftime('%-d %B, %Y'))
    location_string = reg_details.conference.city
    if reg_details.conference.hotel:
        location_string += ' at the ' + reg_details.conference.hotel.name
    canv.drawString(1.7 * inch, 9.52 * inch - 24, location_string)

    # Purchase details
    canv.setFont('Helvetica-Bold', 11)
    canv.drawRightString(1.6 * inch, 8.7 * inch, 'Purchase Date:')
    canv.drawRightString(6.0 * inch, 8.7 * inch, 'Invoice Number:')
    canv.setFont('Helvetica', 11)
    canv.drawString(1.7 * inch, 8.7 * inch,
                    reg_details.register_date.strftime('%-d %B, %Y'))
    invoice_number = str(invoice.pk) if invoice else 'NA'
    canv.drawString(6.1 * inch, 8.7 * inch, invoice_number)
    canv.setFont('Helvetica-Bold', 9)
    if invoice:
        canv.setFont('Helvetica-Bold', 9)
        canv.drawRightString(1.6 * inch, 8.7 * inch - 13, 'Sales Credit:')
        canv.drawRightString(1.6 * inch, 8.7 * inch - 25, 'PD Credit:')
        canv.setFont('Helvetica', 9)
        if invoice.sales_credit.first_name and invoice.sales_credit.last_name:
            sales_name = invoice.sales_credit.first_name + ' ' + \
                invoice.sales_credit.last_name
        else:
            sales_name = invoice.sales_credit.username
        canv.drawString(1.7 * inch, 8.7 * inch - 13, sales_name)
        if reg_details.conference.developer:
            if reg_details.conference.developer.first_name and \
                reg_details.conference.developer.last_name:
                pd_name = reg_details.conference.developer.first_name + ' ' + \
                    reg_details.conference.developer.last_name
            else:
                pd_name = reg_details.conference.developer.username
        else:
            pd_name = 'Not Assigned'
        canv.drawString(1.7 * inch, 8.7 * inch - 25, pd_name)

        if reg_details.registration_status in PAID_STATUS_VALUES:
            canv.setFont('Helvetica-Bold', 9)
            canv.drawRightString(6.0 * inch, 8.7 * inch - 13, 'Payment Method:')
            canv.drawRightString(6.0 * inch, 8.7 * inch - 25, 'Payment Date:')
            canv.setFont('Helvetica', 9)
            canv.drawString(6.1 * inch, 8.7 * inch - 13,
                            invoice.get_payment_method_display())
            canv.drawString(6.1 * inch, 8.7 * inch - 25,
                            invoice.payment_date.strftime('%-d %B, %Y'))
        if reg_details.registration_status in CXL_VALUES:
            canv.setFont('Helvetica-Bold', 9)
            canv.drawRightString(6.0 * inch, 8.7 * inch - 37,
                                 'Cancellation Date:')
            canv.setFont('Helvetica', 9)
            canv.drawString(
                6.1 * inch, 8.7 * inch - 37,
                reg_details.cancellation_date.strftime('%-d %B, %Y')
            )

    # Buyer Details
    canv.setFont('Helvetica-Bold', 11)
    canv.drawRightString(1.6 * inch, 7.7 * inch, 'Sold To:')

    customer_company_details = reg_details.registrant.company.name
    if reg_details.registrant.company.address1:
        customer_company_details += '<br/>'
        customer_company_details += reg_details.registrant.company.address1
    if reg_details.registrant.company.address2:
        customer_company_details += '<br/>'
        customer_company_details += reg_details.registrant.company.address2
    city_line = ''
    if reg_details.registrant.company.city:
        city_line = reg_details.registrant.company.city
    if reg_details.registrant.company.state_prov:
        if len(city_line) > 0:
            city_line += ', '
        city_line += reg_details.registrant.company.state_prov
    if len(city_line) > 0:
        customer_company_details += '<br/>' + city_line
    if reg_details.registrant.company.postal_code:
        customer_company_details += '<br/>'
        customer_company_details += reg_details.registrant.company.postal_code
    if reg_details.registrant.company.country:
        customer_company_details += '<br/>'
        customer_company_details += reg_details.registrant.company.country
    style = ParagraphStyle(
        'default',
        fontName='Helvetica',
        fontSize=11,
        leading=13,
    )
    para = Paragraph(customer_company_details, style)
    h = para.wrap(3.5 * inch, 1.2 * inch)[1]
    para.drawOn(canv, 1.7 * inch, 7.7 * inch - h + 11)

    canv.setFont('Helvetica-Bold', 9)
    canv.drawRightString(6.0 * inch, 7.7 * inch, 'Phone:')
    canv.drawRightString(6.0 * inch, 7.7 * inch - 11, 'Email:')
    canv.drawRightString(1.6 * inch, 6.5 * inch, 'Company ID No:')
    canv.setFont('Helvetica', 9)
    canv.drawString(6.1 * inch, 7.7 * inch, reg_details.registrant.phone1)
    canv.drawString(1.7 * inch, 6.5 * inch,
                    str(reg_details.registrant.company.pk))
    if reg_details.registrant.company.gst_hst_exemption_number:
        canv.setFont('Helvetica-Bold', 9)
        canv.drawRightString(1.6 * inch, 6.2 * inch, 'GST/HST Exemption No:')
        canv.setFont('Helvetica', 9)
        canv.drawString(1.7 * inch, 6.2 * inch,
                        reg_details.registrant.company.gst_hst_exemption_number)
    if reg_details.registrant.company.qst_exemption_number:
        canv.setFont('Helvetica-Bold', 9)
        canv.drawRightString(1.6 * inch, 6.2 * inch - 11, 'QST Exemption No:')
        canv.setFont('Helvetica', 9)
        canv.drawString(1.7 * inch, 6.2 * inch - 11,
                        reg_details.registrant.company.qst_exemption_number)
    # Assistant Details
    if reg_details.registrant.assistant:
        canv.setFont('Helvetica-Bold', 9)
        canv.drawRightString(6.0 * inch, 7.0 * inch, 'Secondary Contact')
        canv.setFont('Helvetica', 9)
        assistant_details = []
        asst_name = ''
        if reg_details.registrant.assistant.salutation:
            asst_name += reg_details.registrant.assistant.salutation
        if reg_details.registrant.assistant.first_name:
            if len(asst_name) > 0:
                asst_name += ' '
            asst_name += reg_details.registrant.assistant.first_name
        if reg_details.registrant.assistant.last_name:
            if len(asst_name) > 0:
                asst_name += ' '
            asst_name += reg_details.registrant.assistant.last_name
        if len(asst_name) > 0:
            assistant_details.append(asst_name)
        if reg_details.registrant.assistant.phone:
            assistant_details.append(reg_details.registrant.assistant.phone)
        if reg_details.registrant.assistant.email:
            assistant_details.append(reg_details.registrant.assistant.email)
        if len(assistant_details) > 0:
            y = 7.0 * inch
            for line in assistant_details:
                canv.drawString(6.1 * inch, y, line)
                y -= 11
    style = ParagraphStyle(
        'default',
        fontName = 'Helvetica',
        fontSize = 9,
        leading = 11,
    )
    para = Paragraph(reg_details.registrant.email1, style)
    h = para.wrap(2.1 * inch, 1 * inch)[1]
    para.drawOn(canv, 6.1 * inch, 7.7 * inch - h - 2)

    # registrant details
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
    name = reg_details.registrant.first_name + ' ' + \
        reg_details.registrant.last_name
    para = Paragraph(name, style)
    h = para.wrap(2.1 * inch, 1 * inch)[1]
    para.drawOn(canv, 0.45 * inch, 5.1 * inch - h + 9)
    reg_option_list = []
    canv.setFont('Helvetica', 9)
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
    y = 5.1 * inch
    for option in reg_option_list:
        canv.drawString(2.75 * inch, y, option)
        y -= 14
    base_amount = invoice.pre_tax_price if invoice else 0
    canv.drawRightString(8.1 * inch, 5.1 * inch, '${:,.2f}'.format(base_amount))

    # notes
    canv.setFont('Helvetica-Bold', 9)
    canv.drawString(0.45 * inch, 4.2 * inch, 'Notes:')
    style = ParagraphStyle(
        'default',
        fontName = 'Helvetica',
        fontSize = 9,
        leading = 11,
    )
    memo_text = ''
    if reg_details.registration_notes:
        memo_text = reg_details.registration_notes
    if invoice:
        if invoice.invoice_notes:
            if len(memo_text) > 0:
                memo_text += '<br/><br/>'
            memo_text += invoice.invoice_notes
        if invoice.sponsorship_description:
            if len(memo_text) > 0:
                memo_text += '<br/><br/>'
            memo_text += invoice.sponsorship_description
    para = Paragraph(memo_text, style)
    h = para.wrap(4 * inch, 2 * inch)[1]
    para.drawOn(canv, 0.45 * inch, 4.2 * inch - h)

    # Cost details
    gst = hst = qst = 0
    if invoice:
        if reg_details.conference.gst_charged:
            gst = base_amount * invoice.gst_rate
        if reg_details.conference.hst_charged:
            hst = base_amount * invoice.hst_rate
        if reg_details.conference.qst_charged:
            qst = base_amount * (1 + invoice.gst_rate) * invoice.qst_rate
    canv.line(6.2 * inch, 4.7 * inch, 8.2 * inch, 4.7 * inch)
    canv.rect(7.2 * inch, 3.3 * inch, 1.0 * inch, 0.5 * inch)
    canv.setFont('Helvetica-Bold', 9)
    canv.drawRightString(7.1 * inch, 4.5 * inch, 'Pre-Tax Total:')
    canv.drawRightString(7.1 * inch, 4.5 * inch - 12, 'GST:')
    canv.drawRightString(7.1 * inch, 4.5 * inch - 24, 'HST:')
    canv.drawRightString(7.1 * inch, 4.5 * inch - 36, 'QST:')
    canv.drawRightString(7.1 * inch, 3.5 * inch, 'Total Invoice:')
    canv.drawRightString(8.1 * inch, 3.5 * inch,
                         '${:,.2f}'.format(base_amount + gst + hst + qst))
    canv.drawRightString(7.1 * inch, 3.1 * inch, 'Currency:')
    if reg_details.conference.billing_currency != 'CAD':
        canv.drawRightString(7.1 * inch, 3.1 * inch - 12, 'BOC Conversion Rate')
        canv.drawRightString(7.1 * inch, 3.1 * inch - 24,
                             'C$ Equivalent (pre-tax)')
        canv.drawRightString(7.1 * inch, 3.1 * inch - 36,
                             'C$ Equivalent (total)')
    canv.setFont('Helvetica', 9)
    canv.drawRightString(8.1 * inch, 4.5 * inch, '${:,.2f}'.format(base_amount))
    canv.drawRightString(8.1 * inch, 4.5 * inch - 12, '${:,.2f}'.format(gst))
    canv.drawRightString(8.1 * inch, 4.5 * inch - 24, '${:,.2f}'.format(hst))
    canv.drawRightString(8.1 * inch, 4.5 * inch - 36, '${:,.2f}'.format(qst))
    canv.drawRightString(8.1 * inch, 3.1 * inch,
                         reg_details.conference.billing_currency)
    if reg_details.conference.billing_currency !='CAD' and invoice:
        canv.drawRightString(8.1 * inch, 3.1 * inch - 12,
                             str(invoice.fx_conversion_rate))
        canv.drawRightString(8.1 * inch, 3.1 * inch - 24,
                             str(base_amount * invoice.fx_conversion_rate))
        canv.drawRightString(8.1 * inch, 3.1 * inch - 36,
                             str((base_amount + hst + gst + qst) *
                                 invoice.fx_conversion_rate))

    # Staff user details
    canv.setFont('Helvetica-Bold', 9)
    canv.drawRightString(1.56 * inch, 0.5 * inch,
                         'Record Created By:')
    canv.drawRightString(1.56 * inch, 0.5 * inch - 12,
                         'Last Modified By:')
    canv.setFont('Helvetica', 9)
    if reg_details.created_by.first_name and reg_details.created_by.last_name:
        add_details = reg_details.created_by.first_name + ' ' + \
            reg_details.created_by.last_name + ' - '
    else:
        add_details = reg_details.created_by.username + ' - '
    add_date = reg_details.date_created.astimezone(
        pytz.timezone('America/Toronto')
    )
    add_details += add_date.strftime('%Y-%m-%d %I:%M:%S %p')
    canv.drawString(1.66 * inch, 0.5 * inch, add_details)
    if reg_details.modified_by.first_name and reg_details.modified_by.last_name:
        modify_details = reg_details.modified_by.first_name + ' ' + \
            reg_details.modified_by.last_name + ' - '
    else:
        modify_details = reg_details.modified_by.username + ' - '
    mod_date = reg_details.date_modified.astimezone(
        pytz.timezone('America/Toronto')
    )
    modify_details += mod_date.strftime('%Y-%m-%d %I:%M:%S %p')
    canv.drawString(1.66 * inch, 0.5 * inch -12, modify_details)
