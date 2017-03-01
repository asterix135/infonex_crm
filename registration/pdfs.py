import os
import pytz

from .constants import *
from infonex_crm.settings import BASE_DIR

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

################
# Generic
################
def insert_generic_report_header(canv, event):
    pass


################
# Delegate List
################
def del_list_first_page(canv, doc):
    PAGE_HEIGHT = letter[1]
    PAGE_WIDTH = letter[0]
    styles=getSampleStyleSheet()
    title = 'Hello World!'
    pageinfo = 'platypus example'

    # call insert generic... here
    canvas.saveState()
    canvas.setFont('Times-Bold', 16)
    canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, title)
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch, 'First Page / %s' % pageinfo)
    canvas.restoreState()


def del_list_later_pages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch, 'Page %d %s' % (doc.page, pageinfo))
    canvas.restoreState()


def generate_delegate_list(story, event, sort='company'):
    pass


################
# No Name list
################
def no_name_list(canv):
    pass


################
# Registration Report
################
def registration_report(canv):
    pass


################
# On Site Report
################
def on_site_report(canv):
    pass


###############
# Unpaid list
###############
def unpaid_list(canv):
    pass


##############
# Phone LIst
##############
def phone_list(canv):
    pass


##############
# Badges
##############
def badges(canv):
    pass


##############
# Big Name Badges
##############
def big_name_badges(canv):
    pass
