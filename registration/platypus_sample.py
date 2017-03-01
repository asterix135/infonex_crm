from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas

PAGE_HEIGHT = letter[1]
PAGE_WIDTH = letter[0]
styles=getSampleStyleSheet()

title = 'Hello World!'
pageinfo = 'platypus example'


def my_first_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Bold', 16)
    canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, title)
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch, 'First Page / %s' % pageinfo)
    canvas.restoreState()


def my_later_pages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch, 'Page %d %s' % (doc.page, pageinfo))
    canvas.restoreState()


def main():
    doc = SimpleDocTemplate('phello.pdf')
    Story = [Spacer(1, 2*inch)]
    style = styles['Normal']
    for i in range(100):
        bogustext = ('This is paragraph number %s.  ' % i) * 20
        p = Paragraph(bogustext, style)
        Story.append(p)
        Story.append(Spacer(1, 0.2 * inch))
    doc.build(Story, onFirstPage = my_first_page, onLaterPages = my_later_pages)


def flowable():
    styleSheet = getSampleStyleSheet()
    style = styleSheet['BodyText']
    P=Paragraph('This is a very silly example'*10,style)
    canv = Canvas('doc.pdf')
    aW = 460    # available width and height
    aH = 800
    w,h = P.wrap(aW, aH)
    if w<=aW and h<=aH:
        P.drawOn(canv,0,aH)
        aH = aH - h
        canv.save()
    else:
       raise ValueError("Not enough room")


def frame_sample():
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']
    story = []
    #add some flowables
    story.append(Paragraph("This is a Heading",styleH))
    story.append(Paragraph("This is a paragraph in <i>Normal</i> style.",
       styleN))
    c  = Canvas('mydoc.pdf')
    f = Frame(inch, inch, 6*inch, 9*inch, showBoundary=1)
    f.addFromList(story,c)
    c.save()


def base_template_sample():
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']
    story = []
    #add some flowables
    story.append(Paragraph("This is a Heading",styleH))
    story.append(Paragraph("This is a paragraph in <i>Normal</i> style.",
       styleN))
    story.append(Paragraph("This is aother paragraph.  It is full of interesting details about how much money you can make by helping Nigerian princes get money out of the country", styleN))
    doc = SimpleDocTemplate('mydoc2.pdf',pagesize = letter)
    doc.build(story)


if __name__ == '__main__':
    # main()
    # flowable()
    # frame_sample()
    base_template_sample()
