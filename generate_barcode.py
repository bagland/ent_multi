from ent.models import Product
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Frame, BaseDocTemplate, PageTemplate
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch, mm, cm
import os
from django.conf import settings

class BarcodePage:
	def __init__(self, company):
		doc = BaseDocTemplate(os.path.join(settings.BASE_DIR, 'new.pdf'))
		pdfmetrics.registerFont(TTFont('OpenSans-Regular', os.path.join(settings.BASE_DIR, 'OpenSans-Regular.ttf')))
		column_gap = 1 * cm
		print(doc.leftMargin)
		print(doc.width)
		print(inch*2)
		doc.addPageTemplates(
			[
				PageTemplate(
					frames = [
						Frame(
							doc.leftMargin,
							doc.bottomMargin,
							doc.width/2,
							doc.height,
							id='left',
							# rightPadding = column_gap/2,
							showBoundary = 1
						),
						Frame(
							doc.leftMargin + doc.width/2,
							doc.bottomMargin,
							doc.width/2,
							doc.height,
							id='right',
							# leftPadding = 0.5 * cm,
							showBoundary = 1
						),
					]
				),
			]
		)

		story = []
		styles = getSampleStyleSheet()
		styleN = styles['Normal']
		styleN.fontName = 'OpenSans-Regular'
		products = Product.objects.filter(had_no_barcode=True, company=company)
		for product in products:
			story.append(Paragraph(product.name, styleN))
			bcd = createBarcodeDrawing('Code128', value=product.barcode, barHeight=9*mm, humanReadable=True)
			story.append(bcd)

		doc.build(story)