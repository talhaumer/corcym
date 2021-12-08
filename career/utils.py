# from io import BytesIO
# from django.http import HttpResponse
# from django.template.loader import get_template
# # from xhtml2pdf import pisa
#
# def render_to_pdf(template_src, context_dict={}, path=''):
# 	template = get_template(template_src)
# 	html  = template.render(context_dict)
# 	result = BytesIO()
# 	with open(path, 'wb+') as output:
# 		pdf = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), output, encoding='UTF-8')
#