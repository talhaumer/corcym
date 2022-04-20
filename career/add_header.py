from functools import partial

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph

styles = getSampleStyleSheet()
styleN = styles["Normal"]
styleH = styles["Heading1"]


def header(canvas, doc, content):
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.topMargin)
    content.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
    canvas.restoreState()


doc = BaseDocTemplate("test.pdf", pagesize=letter)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 2, id="normal")
header_content = Paragraph(
    "This is a multi-line header.  It goes on every page.  " * 8, styleN
)
template = PageTemplate(
    id="test", frames=frame, onPage=partial(header, content=header_content)
)
doc.addPageTemplates([template])

text = []
for i in range(111):
    text.append(Paragraph("This is line %d." % i, styleN))
doc.build(text)
