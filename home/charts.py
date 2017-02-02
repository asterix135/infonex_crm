from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import HorizontalBarChart

class MyBarChartDrawing(Drawing):
    def __init__(self, width=500, height=250, *args, **kw):
        Drawing.__init__(self,width,height,*args,**kw)
        self.add(HorizontalBarChart(), name='chart')

        self.add(String(180,230,'Chart'), name='title')

        #set any shapes, fonts, colors you want here.  We'll just
        #set a title font and place the chart within the drawing
        self.chart.x = 60
        self.chart.y = 20
        self.chart.width = self.width - 70
        self.chart.height = self.height - 45
        self.chart.valueAxis.valueMin = 0

        self.title.fontName = 'Helvetica-Bold'
        self.title.fontSize = 12

        self.chart.data = [[100,150,200,235]]
